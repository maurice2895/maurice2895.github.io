/* Exercise compatibility and fail-open behavior without browser dependencies. */
const { readFileSync } = require('node:fs');
const { join } = require('node:path');
const { runInNewContext } = require('node:vm');
const assert = require('node:assert/strict');
const source = readFileSync(join(__dirname, '..', 'site.js'), 'utf8');

for (const brokenObserver of [false, true]) {
  const visible = new Set();
  const child = {
    classList: { add: name => visible.add(name) },
    style: {},
    getBoundingClientRect: () => ({ top: 1000 }),
  };
  const header = { classList: { toggle() {}, contains: () => false } };
  const toggle = { addEventListener() {}, setAttribute() {} };
  const nav = { addEventListener() {} };
  let legacyListener = false;
  const document = {
    readyState: 'complete',
    documentElement: { classList: { add() {} } },
    querySelector: s => ({ '.header': header, '.nav-toggle': toggle }[s] || null),
    getElementById: () => nav,
    addEventListener() {},
    querySelectorAll: s => s.startsWith('.bento,') ? [{ children: [child] }] :
      s === '.reveal' ? [child] : [],
  };
  const window = {
    innerHeight: 800, scrollY: 0, addEventListener() {},
    matchMedia: () => ({ matches: false, addListener() { legacyListener = true; } }),
    IntersectionObserver: true,
  };
  function IntersectionObserver(callback) {
    if (brokenObserver) throw new Error('Observer unavailable');
    this.observe = target => callback([{ target, isIntersecting: true }]);
    this.unobserve = () => {};
  }
  runInNewContext(source, { document, window, IntersectionObserver });
  assert.equal(legacyListener, true, 'Older media query API must be supported');
  assert.equal(visible.has('is-visible'), true, 'Content must remain visible');
}
console.log('JavaScript behavior checks passed: legacy media API and observer recovery.');
