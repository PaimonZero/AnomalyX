import assert from "node:assert/strict";
import test from "node:test";

import { copyTextWithFeedback } from "./clipboard-copy.ts";

test("copyTextWithFeedback reports success when clipboard write resolves", async () => {
  const messages: string[] = [];
  const clipboard = {
    writeText: async () => undefined,
  };

  await copyTextWithFeedback("curl", "cURL copied.", (message) => messages.push(message), clipboard);

  assert.deepEqual(messages, ["cURL copied."]);
});

test("copyTextWithFeedback reports failure when clipboard write rejects", async () => {
  const messages: string[] = [];
  const clipboard = {
    writeText: async () => {
      throw new Error("Clipboard denied");
    },
  };

  await copyTextWithFeedback("curl", "cURL copied.", (message) => messages.push(message), clipboard);

  assert.deepEqual(messages, ["Could not copy request sample."]);
});
