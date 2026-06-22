import assert from "node:assert/strict";
import test from "node:test";

import { formatRuleTypology, summarizeRuleEngine } from "./rules-detail-format.ts";

test("summarizeRuleEngine reports enabled rule count and version", () => {
  assert.equal(
    summarizeRuleEngine({
      version: 2,
      rules: [
        { id: "R-1", typology: "structuring", severity: "HIGH", enabled: true, condition: "amount > 1" },
        { id: "R-2", typology: "velocity", severity: "MEDIUM", enabled: false, condition: "amount > 2" },
      ],
    }),
    "1/2 enabled · version 2",
  );
});

test("formatRuleTypology falls back to fake backend rule name", () => {
  assert.equal(
    formatRuleTypology({
      id: "R-STRUCT-01",
      name: "Structuring pattern",
      severity: "HIGH",
      enabled: true,
    }),
    "Structuring pattern",
  );
});

test("formatRuleTypology falls back when typology is empty", () => {
  assert.equal(
    formatRuleTypology({
      id: "R-STRUCT-02",
      typology: "",
      name: "Structuring pattern",
      severity: "HIGH",
      enabled: true,
    }),
    "Structuring pattern",
  );
});
