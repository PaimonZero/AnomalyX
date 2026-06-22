import assert from "node:assert/strict";
import test from "node:test";

import { copyTextToClipboard } from "./clipboard.ts";

test("copyTextToClipboard reports success when clipboard write resolves", async () => {
  const clipboard = {
    writeText: async () => undefined,
  };

  assert.equal(await copyTextToClipboard("TX-1", clipboard), true);
});

test("copyTextToClipboard reports failure when clipboard write rejects", async () => {
  const clipboard = {
    writeText: async () => {
      throw new Error("Clipboard denied");
    },
  };

  assert.equal(await copyTextToClipboard("TX-1", clipboard), false);
});
