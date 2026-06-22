import assert from "node:assert/strict";
import test from "node:test";

import { formatHttpStatusBarWidth } from "./monitoring-display-format.ts";

test("formatHttpStatusBarWidth returns zero width when there are no requests", () => {
  assert.equal(formatHttpStatusBarWidth(0, 0), "0%");
});

test("formatHttpStatusBarWidth returns status percentage when requests exist", () => {
  assert.equal(formatHttpStatusBarWidth(25, 100), "25%");
});
