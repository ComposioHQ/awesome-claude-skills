#!/usr/bin/env node
/**
 * gen_excel.mjs — 零依赖 xlsx 生成器（talent-search 专用）
 * 用法: node gen_excel.mjs <candidates.json> <output.xlsx> [sheetName]
 *
 * candidates.json 结构:
 * {
 *   "sheet": "候选清单（可选，默认「候选清单」）",
 *   "candidates": [
 *     {
 *       "name": "张某某 / San Zhang",
 *       "education": "清华大学 计算机本硕（2015-2022）\nCMU CS PhD（2022-2027 在读）",
 *       "experience": "MSRA 研究实习（2020-2021）\nMeta AI Research Intern（2024）",
 *       "homepage": "https://sanzhang.dev 或 未获取",
 *       "github": "https://github.com/sanzhang 或 未获取",
 *       "papers": "一作 4 篇：\n① R-FCN: Object Detection via Region-based Fully Convolutional Networks（NeurIPS 2016）\n② …（≤5 篇） 或 未获取",
 *       "labs": "清华大学 THUNLP（2016-2018）\nStanford NLP Group（2023-） 或留空（没有就不填）",
 *       "highlight": "R-FCN 一作；vLLM 核心贡献者",
 *       "notes": "CV: https://... ｜ LinkedIn: https://... ｜ 邮箱: x@y（论文通讯邮箱） 或 未获取"
 *     }
 *   ]
 * }
 *
 * 输出列（固定 9 列）:
 *   姓名 | 学历 | 实习/工作经历 | 个人主页 | GitHub | 一作论文 | 大学实验室经历 | 匹配亮点 | 备注（CV/联系方式）
 * 特性: 表头加粗灰底居中、数据区自动换行顶对齐、细边框、冻结首行、自动筛选、列宽预设。
 * 数据单元格里的 \n 在 Excel 中显示为行内换行。
 */

import { deflateRawSync } from 'node:zlib';
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { dirname } from 'node:path';

// ---------- 工具函数 ----------

const CRC_TABLE = (() => {
  const t = new Uint32Array(256);
  for (let n = 0; n < 256; n++) {
    let c = n;
    for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
    t[n] = c >>> 0;
  }
  return t;
})();

function crc32(buf) {
  let c = 0xffffffff;
  for (let i = 0; i < buf.length; i++) c = CRC_TABLE[(c ^ buf[i]) & 0xff] ^ (c >>> 8);
  return (c ^ 0xffffffff) >>> 0;
}

function dosDateTime(d = new Date()) {
  return {
    time: (d.getHours() << 11) | (d.getMinutes() << 5) | (d.getSeconds() >> 1),
    date: ((d.getFullYear() - 1980) << 9) | ((d.getMonth() + 1) << 5) | d.getDate(),
  };
}

/** XML 文本转义：去非法控制字符，转义 & < > " */
function esc(s) {
  return String(s ?? '')
    .replace(/[\x00-\x08\x0b\x0c\x0e-\x1f]/g, '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

/** sheet 名清洗：Excel 不允许 : \ / ? * [ ]，最长 31 字符 */
function sheetName(s) {
  return (s || '候选清单').replace(/[:\\/?*[\]]/g, ' ').trim().slice(0, 31) || '候选清单';
}

/** 最小 zip 打包（deflate），entries: [{name, data(Buffer)}] */
function zip(entries) {
  const chunks = [];
  const central = [];
  let offset = 0;
  const { time, date } = dosDateTime();
  for (const f of entries) {
    const nameBuf = Buffer.from(f.name, 'utf8');
    const crc = crc32(f.data);
    const comp = deflateRawSync(f.data);

    const lh = Buffer.alloc(30);
    lh.writeUInt32LE(0x04034b50, 0);
    lh.writeUInt16LE(20, 4); // version needed
    lh.writeUInt16LE(0x0800, 6); // flags: UTF-8 文件名
    lh.writeUInt16LE(8, 8); // method: deflate
    lh.writeUInt16LE(time, 10);
    lh.writeUInt16LE(date, 12);
    lh.writeUInt32LE(crc, 14);
    lh.writeUInt32LE(comp.length, 18);
    lh.writeUInt32LE(f.data.length, 22);
    lh.writeUInt16LE(nameBuf.length, 26);
    lh.writeUInt16LE(0, 28); // extra len
    chunks.push(lh, nameBuf, comp);

    const ch = Buffer.alloc(46);
    ch.writeUInt32LE(0x02014b50, 0);
    ch.writeUInt16LE(20, 4); // version made by
    ch.writeUInt16LE(20, 6); // version needed
    ch.writeUInt16LE(0x0800, 8); // flags
    ch.writeUInt16LE(8, 10); // method
    ch.writeUInt16LE(time, 12);
    ch.writeUInt16LE(date, 14);
    ch.writeUInt32LE(crc, 16);
    ch.writeUInt32LE(comp.length, 20);
    ch.writeUInt32LE(f.data.length, 24);
    ch.writeUInt16LE(nameBuf.length, 28);
    ch.writeUInt16LE(0, 30); // extra
    ch.writeUInt16LE(0, 32); // comment
    ch.writeUInt16LE(0, 34); // disk
    ch.writeUInt16LE(0, 36); // internal attrs
    ch.writeUInt32LE(0, 38); // external attrs
    ch.writeUInt32LE(offset, 42);
    central.push(ch, nameBuf);

    offset += 30 + nameBuf.length + comp.length;
  }
  const cdSize = central.reduce((s, b) => s + b.length, 0);
  const eocd = Buffer.alloc(22);
  eocd.writeUInt32LE(0x06054b50, 0);
  eocd.writeUInt16LE(0, 4);
  eocd.writeUInt16LE(0, 6);
  eocd.writeUInt16LE(entries.length, 8);
  eocd.writeUInt16LE(entries.length, 10);
  eocd.writeUInt32LE(cdSize, 12);
  eocd.writeUInt32LE(offset, 16);
  eocd.writeUInt16LE(0, 20);
  return Buffer.concat([...chunks, ...central, eocd]);
}

// ---------- xlsx 各 XML 部件 ----------

const XML_HEAD = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n';

function contentTypesXml() {
  return (
    XML_HEAD +
    '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">' +
    '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>' +
    '<Default Extension="xml" ContentType="application/xml"/>' +
    '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>' +
    '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>' +
    '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>' +
    '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>' +
    '<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>' +
    '</Types>'
  );
}

function relsXml() {
  return (
    XML_HEAD +
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">' +
    '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>' +
    '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>' +
    '<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>' +
    '</Relationships>'
  );
}

function workbookXml(sheet) {
  return (
    XML_HEAD +
    '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">' +
    `<sheets><sheet name="${esc(sheet)}" sheetId="1" r:id="rId1"/></sheets>` +
    '</workbook>'
  );
}

function workbookRelsXml() {
  return (
    XML_HEAD +
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">' +
    '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>' +
    '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>' +
    '</Relationships>'
  );
}

function stylesXml() {
  return (
    XML_HEAD +
    '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">' +
    '<fonts count="2">' +
    '<font><sz val="11"/><name val="等线"/></font>' +
    '<font><b/><sz val="11"/><name val="等线"/></font>' +
    '</fonts>' +
    '<fills count="3">' +
    '<fill><patternFill patternType="none"/></fill>' +
    '<fill><patternFill patternType="gray125"/></fill>' +
    '<fill><patternFill patternType="solid"><fgColor rgb="FFF2F2F2"/><bgColor indexed="64"/></patternFill></fill>' +
    '</fills>' +
    '<borders count="2">' +
    '<border><left/><right/><top/><bottom/><diagonal/></border>' +
    '<border><left style="thin"><color rgb="FFD9D9D9"/></left><right style="thin"><color rgb="FFD9D9D9"/></right>' +
    '<top style="thin"><color rgb="FFD9D9D9"/></top><bottom style="thin"><color rgb="FFD9D9D9"/></bottom><diagonal/></border>' +
    '</borders>' +
    '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>' +
    '<cellXfs count="2">' +
    '<xf numFmtId="0" fontId="0" fillId="0" borderId="1" xfId="0" applyAlignment="1" applyBorder="1">' +
    '<alignment horizontal="left" vertical="top" wrapText="1"/></xf>' +
    '<xf numFmtId="0" fontId="1" fillId="2" borderId="1" xfId="0" applyAlignment="1" applyFont="1" applyFill="1" applyBorder="1">' +
    '<alignment horizontal="center" vertical="center" wrapText="1"/></xf>' +
    '</cellXfs>' +
    '<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>' +
    '</styleSheet>'
  );
}

const HEADERS = ['姓名', '学历', '实习/工作经历', '个人主页', 'GitHub', '一作论文', '大学实验室经历', '匹配亮点', '备注（CV/联系方式）'];
const COL_WIDTHS = [16, 45, 60, 38, 34, 55, 32, 45, 45];
const FIELD_ORDER = ['name', 'education', 'experience', 'homepage', 'github', 'papers', 'labs', 'highlight', 'notes'];

function sheetXml(rows) {
  const col = (i, w) => `<col min="${i}" max="${i}" width="${w}" customWidth="1"/>`;
  const cols = `<cols>${COL_WIDTHS.map((w, i) => col(i + 1, w)).join('')}</cols>`;
  const cell = (ref, text, style) =>
    `<c r="${ref}" s="${style}" t="inlineStr"><is><t xml:space="preserve">${esc(text)}</t></is></c>`;
  const row = (r, cells, style) =>
    `<row r="${r}">${cells.map((text, i) => cell(`${colName(i)}${r}`, text, style)).join('')}</row>`;

  const headerRow = row(1, HEADERS, 1);
  // labs 缺省留空（「有才写」语义），其余字段缺省填「未获取」
  const dataRows = rows.map((r, idx) =>
    row(idx + 2, FIELD_ORDER.map((f) => r[f] ?? (f === 'labs' ? '' : '未获取')), 0)
  );
  const lastRow = rows.length + 1;

  return (
    XML_HEAD +
    '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">' +
    '<sheetViews><sheetView workbookViewId="0"><pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/></sheetView></sheetViews>' +
    cols +
    `<sheetData>${headerRow}${dataRows.join('')}</sheetData>` +
    `<autoFilter ref="A1:${colName(HEADERS.length - 1)}${lastRow}"/>` +
    '</worksheet>'
  );
}

function colName(i) {
  let s = '';
  for (let n = i; n >= 0; n = Math.floor(n / 26) - 1) s = String.fromCharCode(65 + (n % 26)) + s;
  return s;
}

function coreXml() {
  const now = new Date().toISOString();
  return (
    XML_HEAD +
    '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" ' +
    'xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" ' +
    'xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">' +
    '<dc:creator>Claude Code talent-search</dc:creator>' +
    '<cp:lastModifiedBy>Claude Code talent-search</cp:lastModifiedBy>' +
    `<dcterms:created xsi:type="dcterms:W3CDTF">${now}</dcterms:created>` +
    `<dcterms:modified xsi:type="dcterms:W3CDTF">${now}</dcterms:modified>` +
    '</cp:coreProperties>'
  );
}

function appXml() {
  return (
    XML_HEAD +
    '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" ' +
    'xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">' +
    '<Application>Claude Code talent-search</Application>' +
    '</Properties>'
  );
}

// ---------- 主流程 ----------

function main() {
  const [inputPath, outputPath, sheetArg] = process.argv.slice(2);
  if (!inputPath || !outputPath) {
    console.error('用法: node gen_excel.mjs <candidates.json> <output.xlsx> [sheetName]');
    process.exit(1);
  }

  let input;
  try {
    input = JSON.parse(readFileSync(inputPath, 'utf8'));
  } catch (e) {
    console.error(`读取或解析 ${inputPath} 失败: ${e.message}`);
    process.exit(1);
  }
  if (!Array.isArray(input.candidates) || input.candidates.length === 0) {
    console.error('JSON 中缺少非空的 candidates 数组');
    process.exit(1);
  }

  const sheet = sheetName(sheetArg || input.sheet);
  const parts = [
    { name: '[Content_Types].xml', data: Buffer.from(contentTypesXml(), 'utf8') },
    { name: '_rels/.rels', data: Buffer.from(relsXml(), 'utf8') },
    { name: 'xl/workbook.xml', data: Buffer.from(workbookXml(sheet), 'utf8') },
    { name: 'xl/_rels/workbook.xml.rels', data: Buffer.from(workbookRelsXml(), 'utf8') },
    { name: 'xl/styles.xml', data: Buffer.from(stylesXml(), 'utf8') },
    { name: 'xl/worksheets/sheet1.xml', data: Buffer.from(sheetXml(input.candidates), 'utf8') },
    { name: 'docProps/core.xml', data: Buffer.from(coreXml(), 'utf8') },
    { name: 'docProps/app.xml', data: Buffer.from(appXml(), 'utf8') },
  ];

  const dir = dirname(outputPath);
  if (dir && dir !== '.') mkdirSync(dir, { recursive: true });

  writeFileSync(outputPath, zip(parts));
  console.log(`已生成: ${outputPath}（${input.candidates.length} 位候选人，sheet「${sheet}」）`);
}

main();
