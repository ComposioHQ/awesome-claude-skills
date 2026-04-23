import fs from 'fs';
import path from 'path';
import {
    parseFigmaUrl, executeFigmaAndImagesActions, figmaTool, downloadImage,
    extractNodePositionsHierarchical, generateStructurePrompt, extractJSON,
    postProcessStructure, extractComponentGroups, simplifyFigmaNodeForContent,
    extractDataListPrompt,
    flattenPostOrder, detectRenderingModes, generateFramePrompt, generateComponentPrompt,
    DEFAULT_STYLING, saveGeneratedCode, workspaceManager,
    toKebabCase, toPascalCase, INITIAL_AGENT_SYSTEM_PROMPT, initialAgentInstruction
} from 'coderio';

const [,, command, ...args] = process.argv;
const appPath = process.cwd();
const processDir = path.join(appPath, 'process');
const scriptsDir = path.join(appPath, 'scripts');
const assetsDir = path.join(appPath, 'src/assets');

// Ensure directories exist
[processDir, scriptsDir, assetsDir].forEach(d => {
    if (!fs.existsSync(d)) fs.mkdirSync(d, { recursive: true });
});

function extractAllComponentGroups(node) {
    const groups = new Map();
    function traverse(currentNode) {
        const localGroups = extractComponentGroups(currentNode);
        for (const [name, list] of localGroups) {
            if (!groups.has(name)) groups.set(name, []);
            groups.get(name).push(...list);
        }
        if (currentNode.children) {
            currentNode.children.forEach(traverse);
        }
    }
    traverse(node);
    return groups;
}

function findParentOfGroup(root, componentName) {
    let result = null;
    function traverse(node) {
        if (result) return;
        if (node.children && node.children.some(c => c.data.componentName === componentName)) {
            result = node;
            return;
        }
        if (node.children) node.children.forEach(traverse);
    }
    traverse(root);
    return result;
}

function applyPropsAndStateToProtocol(parsed, node, compName, group, isList) {
    if (parsed && parsed.state && Array.isArray(parsed.state)) {
        if (isList) {
            if (!node.data.states) {
                node.data.states = [];
            }

            node.data.states = node.data.states.filter(s => s.componentName !== compName);

            node.data.states.push({
                state: parsed.state,
                componentName: compName,
                componentPath: group[0]?.data.componentPath || '',
            });

            const originalChildren = node.children || [];
            const newChildren = [];
            const processedComponentNames = new Set();

            for (const child of originalChildren) {
                const childName = child.data.componentName;
                if (childName === compName) {
                    if (!processedComponentNames.has(childName)) {
                        child.data.name = childName;
                        child.id = childName;
                        const cleanKebabName = toKebabCase(childName);
                        child.data.kebabName = cleanKebabName;
                        delete child.data.path;

                        if (parsed.props && Array.isArray(parsed.props)) {
                            child.data.props = parsed.props;
                        }

                        newChildren.push(child);
                        processedComponentNames.add(childName);
                    }
                } else {
                    newChildren.push(child);
                }
            }

            node.children = newChildren;
        }
    }
}

async function main() {
    try {
        switch (command) {
            case 'scaffold-prompt': {
                console.log(INITIAL_AGENT_SYSTEM_PROMPT);
                console.log('\n--- INSTRUCTION ---\n');
                console.log(initialAgentInstruction({ appPath, appName: args[0] || 'MyApp' }));
                break;
            }

            case 'fetch-figma': {
                const [figmaUrl, figmaToken] = args;
                if (!figmaUrl || !figmaToken) throw new Error('Usage: fetch-figma <url> <token>');

                const urlInfo = parseFigmaUrl(figmaUrl);
                console.log('Fetching Figma document...');
                const { document, imageNodesMap } = await executeFigmaAndImagesActions(urlInfo, assetsDir, processDir, figmaToken);

                const simplified = figmaTool.simplifyImageNodes(document, imageNodesMap);
                const processed = figmaTool.processedStyle(simplified);
                fs.writeFileSync(path.join(processDir, 'processed.json'), JSON.stringify(processed, null, 2));

                if (processed.thumbnailUrl) {
                    console.log('Downloading thumbnail...');
                    const base64 = await downloadImage(processed.thumbnailUrl, undefined, undefined, true);
                    fs.writeFileSync(path.join(processDir, 'thumbnail.png'), Buffer.from(base64, 'base64'));
                    console.log('Thumbnail saved to process/thumbnail.png');
                }
                console.log('Figma data processed.');
                break;
            }

            case 'structure-prompt': {
                const procDoc = JSON.parse(fs.readFileSync(path.join(processDir, 'processed.json'), 'utf-8'));
                const frames = procDoc.frames || procDoc.children;
                const positions = extractNodePositionsHierarchical(frames);
                const prompt = generateStructurePrompt({
                    positions: JSON.stringify(positions, null, 2),
                    width: String(procDoc.absoluteBoundingBox?.width || 1440)
                });
                console.log(prompt);
                break;
            }

            case 'save-structure': {
                const structureJson = fs.readFileSync(path.join(scriptsDir, 'structure-output.json'), 'utf-8');
                const pDoc = JSON.parse(fs.readFileSync(path.join(processDir, 'processed.json'), 'utf-8'));

                const parsed = JSON.parse(extractJSON(structureJson));
                const structFrames = pDoc.frames || pDoc.children;
                postProcessStructure(parsed, structFrames);

                const protocol = Array.isArray(parsed) ? parsed[0] : parsed;
                fs.writeFileSync(path.join(processDir, 'protocol.json'), JSON.stringify(protocol, null, 2));
                console.log('Structure saved to process/protocol.json');
                break;
            }

            case 'list-components': {
                const prot = JSON.parse(fs.readFileSync(path.join(processDir, 'protocol.json'), 'utf-8'));
                const groups = extractAllComponentGroups(prot);
                const list = Array.from(groups.keys()).map(name => {
                    return { name, count: groups.get(name).length };
                });
                fs.writeFileSync(path.join(scriptsDir, 'component-list.json'), JSON.stringify(list, null, 2));
                console.log(JSON.stringify(list, null, 2));
                break;
            }

            case 'props-prompt': {
                const compName = args[0];
                const prot2 = JSON.parse(fs.readFileSync(path.join(processDir, 'protocol.json'), 'utf-8'));
                const groups2 = extractAllComponentGroups(prot2);
                const group = groups2.get(compName);
                if (!group) throw new Error(`Component ${compName} not found`);

                const instances = group.flatMap(g => g.data.elements || []);
                const simpleNodes = instances
                    .filter(n => typeof n === 'object' && n !== null)
                    .map(n => simplifyFigmaNodeForContent(n));

                console.log(extractDataListPrompt({
                    containerName: prot2.data.name || 'Container',
                    childComponentName: compName,
                    figmaData: JSON.stringify(simpleNodes, null, 2)
                }));
                break;
            }

            case 'save-props': {
                const cName = args[0];
                const propsJsonPath = path.join(scriptsDir, `${cName}-props.json`);
                const propsJson = fs.readFileSync(propsJsonPath, 'utf-8');
                const parsedProps = JSON.parse(extractJSON(propsJson));

                if (!parsedProps.props || parsedProps.props.length === 0) {
                    throw new Error('Validation Failed: Props array is empty.');
                }

                const prot3 = JSON.parse(fs.readFileSync(path.join(processDir, 'protocol.json'), 'utf-8'));
                const groups3 = extractAllComponentGroups(prot3);
                const group3 = groups3.get(cName);

                const parentNode = findParentOfGroup(prot3, cName);
                if (parentNode) {
                    applyPropsAndStateToProtocol(parsedProps, parentNode, cName, group3, true);
                    fs.writeFileSync(path.join(processDir, 'protocol.json'), JSON.stringify(prot3, null, 2));
                    console.log(`Props applied to ${cName} (Parent: ${parentNode.data.name || parentNode.id})`);
                } else {
                    console.error(`Parent not found for ${cName}`);
                }
                break;
            }

            case 'list-gen-tasks': {
                const prot4 = JSON.parse(fs.readFileSync(path.join(processDir, 'protocol.json'), 'utf-8'));
                const flat = flattenPostOrder(prot4);
                const tasks = flat.map((node, i) => ({
                    index: i,
                    name: node.data.name || node.data.componentName,
                    path: node.data.path || node.data.componentPath,
                    isLeaf: !node.children?.length
                }));
                fs.writeFileSync(path.join(scriptsDir, 'gen-tasks.json'), JSON.stringify(tasks, null, 2));
                console.log(JSON.stringify(tasks, null, 2));
                break;
            }

            case 'code-prompt': {
                const idx = parseInt(args[0]);
                const prot5 = JSON.parse(fs.readFileSync(path.join(processDir, 'protocol.json'), 'utf-8'));
                const flat2 = flattenPostOrder(prot5);
                const node = flat2[idx];
                const assets = fs.readdirSync(assetsDir).join(', ');

                let prompt = '';
                if (!node.children?.length) {
                    prompt = generateComponentPrompt({
                        componentName: node.data.name || node.data.componentName,
                        componentDetails: JSON.stringify(node.data, null, 2),
                        styling: JSON.stringify(DEFAULT_STYLING),
                        assetFiles: assets
                    });
                } else {
                    const imports = node.children.map(c => ({
                        name: c.data.name,
                        path: c.data.path || c.data.componentPath
                    }));
                    const modes = detectRenderingModes(node);
                    prompt = generateFramePrompt({
                        frameDetails: JSON.stringify(node.data, null, 2),
                        childrenImports: JSON.stringify(imports, null, 2),
                        styling: JSON.stringify(DEFAULT_STYLING),
                        assetFiles: assets,
                        renderingModes: modes
                    });
                }

                // Add instruction for Asset Imports in State
                if (node.data.states && node.data.states.length > 0) {
                    prompt += `\n\n<asset_imports_instruction>
The 'states' data contains references to assets (e.g. "@/assets/foo.png").
You MUST:
1. Import these assets at the top of the file: \`import image_foo from '@/assets/foo.png';\`
2. In the \`states\` array in your code, use the variable \`image_foo\` instead of the string.
   Example: \`imageSrc: image_foo\` (NOT \`imageSrc: "@/assets/foo.png"\`)
</asset_imports_instruction>`;
                }

                console.log(prompt);
                break;
            }

            case 'save-code': {
                const idx2 = parseInt(args[0]);
                const codePath = path.join(scriptsDir, 'code-output.txt');
                const code = fs.readFileSync(codePath, 'utf-8');

                const prot6 = JSON.parse(fs.readFileSync(path.join(processDir, 'protocol.json'), 'utf-8'));
                const flat3 = flattenPostOrder(prot6);
                const node2 = flat3[idx2];

                const componentPath = node2.data.path || node2.data.componentPath;
                if (!componentPath) throw new Error(`Node ${node2.data.name} has no path`);

                const compDir = path.join(appPath, 'src', workspaceManager.resolveComponentPath(componentPath));
                saveGeneratedCode(code, compDir);
                console.log(`Code saved to ${compDir}`);
                break;
            }

            default:
                console.log('Unknown command');
        }
    } catch (e) {
        console.error('Error:', e.message);
        process.exit(1);
    }
}

main();
