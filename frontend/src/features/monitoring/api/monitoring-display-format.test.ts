import assert from "node:assert/strict";
import test from "node:test";

import { formatHttpStatusBarWidth, hasChartThreshold } from "./monitoring-display-format.ts";

test("formatHttpStatusBarWidth returns zero width when there are no requests", () => {
  assert.equal(formatHttpStatusBarWidth(0, 0), "0%");
});

test("formatHttpStatusBarWidth returns status percentage when requests exist", () => {
  assert.equal(formatHttpStatusBarWidth(25, 100), "25%");
});

test("hasChartThreshold treats zero as a displayable threshold", () => {
  assert.equal(hasChartThreshold(0), true);
});

test("hasChartThreshold excludes missing thresholds", () => {
  assert.equal(hasChartThreshold(undefined), false);
  assert.equal(hasChartThreshold(null), false);
});
