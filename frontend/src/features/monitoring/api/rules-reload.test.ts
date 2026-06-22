import assert from "node:assert/strict";
import test from "node:test";

import { formatReloadRulesSuccess } from "./rules-reload-format.ts";

test("formatReloadRulesSuccess includes active rule count and version", () => {
  assert.equal(
    formatReloadRulesSuccess({ status: "reloaded", active_rules: 7, version: "rules-v2" }),
    "Backend rules reloaded successfully. 7 active rules · version rules-v2.",
  );
});
