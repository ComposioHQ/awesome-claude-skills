#!/usr/bin/env node
import { existsSync, readFileSync, realpathSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

// This checks stored geometry; it neither renders text nor changes the scene.
const SHAFT_CLEARANCE = 24;
const normalizedText = text => String(text || '').trim().replace(/\s+/g, ' ').toLowerCase();
const unrotated = el => Math.abs(el.angle || 0) < 0.001;
function bounds(el) {
  if (!el || !unrotated(el) || !['x', 'y', 'width', 'height'].every(k => Number.isFinite(el[k])) || el.width <= 0 || el.height <= 0) return null;
  return { left: el.x, right: el.x + el.width, top: el.y, bottom: el.y + el.height };
}
function overlaps(a, b) {
  return a.left < b.right && a.right > b.left && a.top < b.bottom && a.bottom > b.top;
}
function distance(a, b) {
  return Math.hypot(Math.max(0, a.left - b.right, b.left - a.right), Math.max(0, a.top - b.bottom, b.top - a.bottom));
}
function straightAxis(edge) {
  if (!unrotated(edge) || !Number.isFinite(edge.x) || !Number.isFinite(edge.y) || !Array.isArray(edge.points) || edge.points.length !== 2) return null;
  const [start, end] = edge.points;
  if (![start, end].every(p => Array.isArray(p) && p.length === 2 && p.every(Number.isFinite))) return null;
  const dx = Math.abs(end[0] - start[0]);
  const dy = Math.abs(end[1] - start[1]);
  if (dx > 0 && dy <= 4 && dy / dx < 0.05) return { start: edge.x + Math.min(start[0], end[0]), end: edge.x + Math.max(start[0], end[0]), low: 'left', high: 'right' };
  if (dy > 0 && dx <= 4 && dx / dy < 0.05) return { start: edge.y + Math.min(start[1], end[1]), end: edge.y + Math.max(start[1], end[1]), low: 'top', high: 'bottom' };
  return null;
}

export function checkLayout(scene) {
  if (!Array.isArray(scene?.elements)) throw new Error('Expected an exported .excalidraw scene with an elements array.');
  const elements = scene.elements.filter(el => !el?.isDeleted);
  const ids = new Set();
  for (const el of elements) {
    if (!el || typeof el.id !== 'string' || !el.id || typeof el.type !== 'string' || ids.has(el.id)) throw new Error('Scene elements must have unique IDs and types.');
    ids.add(el.id);
  }
  const byId = new Map(elements.map(el => [el.id, el]));
  const texts = elements.filter(el => el.type === 'text' && normalizedText(el.text));
  const boundTextIds = new Set(elements.flatMap(el => (el.boundElements || []).filter(b => b.type === 'text').map(b => b.id)));
  const freeTexts = texts.filter(el => !el.containerId && !boundTextIds.has(el.id));
  const shapes = elements.filter(el => ['rectangle', 'diamond', 'ellipse'].includes(el.type));
  const issues = [];
  const manual = new Map();
  let checkedConnectors = 0;
  const review = (id, reason) => manual.set(id, { elementId: id, reason });
  const issue = (code, elementIds, message) => issues.push({ code, elementIds, message });

  for (const edge of elements.filter(el => el.type === 'arrow')) {
    const referenced = new Set((edge.boundElements || []).filter(b => b.type === 'text').map(b => b.id));
    const labels = texts.filter(el => el.containerId === edge.id || referenced.has(el.id));
    if (!labels.length) {
      if (edge.text || edge.label?.text || referenced.size) review(edge.id, 'Label bounds unavailable; export the scene after rendering or browser sync.');
      continue;
    }
    if (labels.length > 1) issue('multiple-labels', [edge.id, ...labels.map(l => l.id)], 'More than one text element is attached to this connector.');
    const axis = straightAxis(edge);
    if (!axis) review(edge.id, 'Bent, diagonal, rotated, or unmeasured connector: visually check label placement and arrow clearance.');
    else checkedConnectors++;

    for (const label of labels) {
      const labelBox = bounds(label);
      if (!labelBox) {
        review(label.id, 'Label has missing dimensions or rotation; inspect its rendered bounds.');
        continue;
      }
      for (const other of freeTexts) {
        const otherBox = bounds(other);
        if (normalizedText(label.text) !== normalizedText(other.text)) continue;
        if (!otherBox) { review(other.id, 'Matching standalone text has unmeasured bounds; check for a duplicate label.'); continue; }
        if (distance(labelBox, otherBox) <= Math.max(64, (label.fontSize || 20) * 3)) {
          issue('duplicate-label', [edge.id, label.id, other.id], 'A nearby standalone text element repeats the connector label; keep one representation.');
        }
      }
      for (const shape of shapes) {
        const shapeBox = bounds(shape);
        if (shapeBox && overlaps(labelBox, shapeBox)) issue('label-overlap', [edge.id, label.id, shape.id], 'Connector label bounds overlap a node; increase spacing or reposition the label.');
      }
      if (axis) {
        const available = axis.end - axis.start;
        const required = labelBox[axis.high] - labelBox[axis.low] + 2 * SHAFT_CLEARANCE;
        const clearance = Math.min(labelBox[axis.low] - axis.start, axis.end - labelBox[axis.high]);
        if (clearance < SHAFT_CLEARANCE) {
          issue('connector-space', [edge.id, label.id], `Keep at least ${SHAFT_CLEARANCE}px of visible connector on each side of its label. Span ${Math.round(available)}px; minimum ${Math.ceil(required)}px with this label centered.`);
        }
        for (const binding of [edge.startBinding, edge.endBinding]) {
          const node = byId.get(binding?.elementId);
          if (binding?.elementId && (!node || !bounds(node))) review(edge.id, 'Endpoint bounds unavailable or rotated; visually check node clearance.');
        }
      }
    }
  }
  return { checkedConnectors, issues, manualReview: [...manual.values()] };
}

// Skills installers can expose this file through an agent-directory symlink.
const isMain = process.argv[1] && existsSync(process.argv[1])
  && realpathSync(process.argv[1]) === realpathSync(fileURLToPath(import.meta.url));
if (isMain) {
  try {
    if (process.argv.length !== 3) throw new Error('Usage: node check-layout.mjs /absolute/path/board.excalidraw');
    const report = checkLayout(JSON.parse(readFileSync(process.argv[2], 'utf8')));
    console.log(JSON.stringify(report, null, 2));
    process.exitCode = report.issues.length || report.manualReview.length ? 1 : 0;
  } catch (error) {
    console.error(error.message);
    process.exitCode = 2;
  }
}
