import '@testing-library/jest-dom/vitest';
import { cleanup } from '@testing-library/react';
import { afterEach } from 'vitest';

afterEach(() => {
  cleanup();
});

// __sdlc_dom_env_shim__: jsdom implements no layout engine and none of the
// observer APIs that charting / responsive components depend on. recharts'
// <ResponsiveContainer> reads ResizeObserver and the element box; in jsdom
// ResizeObserver is undefined (it throws inside ResponsiveContainer) and the
// box is 0x0 (the chart renders nothing, so content assertions fail).
// Provide minimal, deterministic implementations so charts render at a real
// size under test.
if (typeof globalThis.ResizeObserver === "undefined") {
  globalThis.ResizeObserver = class {
    observe() {}
    unobserve() {}
    disconnect() {}
  };
}
if (typeof globalThis.IntersectionObserver === "undefined") {
  globalThis.IntersectionObserver = class {
    constructor() {}
    observe() {}
    unobserve() {}
    disconnect() {}
    takeRecords() {
      return [];
    }
  };
}
if (typeof window !== "undefined" && !window.matchMedia) {
  window.matchMedia = (query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener() {},
    removeListener() {},
    addEventListener() {},
    removeEventListener() {},
    dispatchEvent() {
      return false;
    },
  });
}
// A non-zero box lets <ResponsiveContainer> (and any offsetWidth reader)
// compute a real size instead of collapsing to 0x0.
if (typeof window !== "undefined" && window.HTMLElement) {
  Object.defineProperty(window.HTMLElement.prototype, "offsetWidth", {
    configurable: true,
    get() {
      return 800;
    },
  });
  Object.defineProperty(window.HTMLElement.prototype, "offsetHeight", {
    configurable: true,
    get() {
      return 600;
    },
  });
  window.HTMLElement.prototype.getBoundingClientRect = function () {
    return {
      width: 800,
      height: 600,
      top: 0,
      left: 0,
      right: 800,
      bottom: 600,
      x: 0,
      y: 0,
      toJSON() {},
    };
  };
}
