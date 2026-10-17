import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';

const [library, readingOrder] = await Promise.all([
  readFile(new URL('../public/library.json', import.meta.url), 'utf8').then(JSON.parse),
  readFile(new URL('../public/reading-order.json', import.meta.url), 'utf8').then(JSON.parse),
]);

function requireText(value, label) {
  assert.equal(typeof value, 'string', `${label} must be a string`);
  assert.ok(value.trim(), `${label} must not be empty`);
  assert.equal(value, value.trim(), `${label} must not have surrounding whitespace`);
}

requireText(readingOrder.title, 'Reading-library title');
requireText(readingOrder.description, 'Reading-library description');
assert.ok(Array.isArray(library.cards) && library.cards.length > 0, 'Library must contain cards');
assert.ok(Array.isArray(readingOrder.chapters) && readingOrder.chapters.length > 0, 'Reading order must contain chapters');

const libraryIds = new Set();
for (const card of library.cards) {
  requireText(card.id, 'Library card ID');
  assert.ok(!libraryIds.has(card.id), `Library contains duplicate card ID: ${card.id}`);
  libraryIds.add(card.id);
}

const chapterIds = new Set();
const chapterTitles = new Set();
const assignments = new Map();
const completedParts = new Set();
let currentPart;

for (const [index, chapter] of readingOrder.chapters.entries()) {
  const label = `Chapter ${index + 1}`;
  assert.ok(chapter && typeof chapter === 'object' && !Array.isArray(chapter), `${label} must be an object`);
  requireText(chapter.id, `${label} ID`);
  assert.match(chapter.id, /^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$/, `${label} ID must be a lowercase kebab-case anchor`);
  assert.ok(!chapterIds.has(chapter.id), `Duplicate chapter ID: ${chapter.id}`);
  chapterIds.add(chapter.id);

  requireText(chapter.title, `${label} title`);
  requireText(chapter.part, `${label} part`);
  requireText(chapter.description, `${label} description`);
  const normalizedTitle = chapter.title.toLowerCase();
  assert.ok(!chapterTitles.has(normalizedTitle), `Duplicate chapter title: ${chapter.title}`);
  chapterTitles.add(normalizedTitle);

  // A part is a continuous reading block; it should not disappear and reappear.
  if (chapter.part !== currentPart) {
    if (currentPart !== undefined) completedParts.add(currentPart);
    assert.ok(!completedParts.has(chapter.part), `Part is split across the reading order: ${chapter.part}`);
    currentPart = chapter.part;
  }

  assert.ok(Array.isArray(chapter.cardIds) && chapter.cardIds.length > 0, `${label} must contain at least one card`);
  for (const id of chapter.cardIds) {
    requireText(id, `${label} card ID`);
    assert.ok(libraryIds.has(id), `Unknown card ID in ${chapter.id}: ${id}`);
    assert.ok(!assignments.has(id), `Card ${id} appears in both ${assignments.get(id)} and ${chapter.id}`);
    assignments.set(id, chapter.id);
  }
}

const missing = [...libraryIds].filter(id => !assignments.has(id));
assert.deepEqual(missing, [], `Cards missing from reading order: ${missing.join(', ')}`);
assert.equal(assignments.size, libraryIds.size, 'Every library card must appear exactly once');

console.log(`Reading order verified: ${assignments.size} cards, ${chapterIds.size} nonempty chapters, ${completedParts.size + 1} continuous parts.`);
console.log('All library IDs are preserved, covered exactly once, and assigned to valid unique chapter anchors.');
