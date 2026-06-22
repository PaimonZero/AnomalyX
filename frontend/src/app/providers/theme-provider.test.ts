import assert from "node:assert/strict";
import test from "node:test";

import { applyTheme, getInitialTheme, getThemeColor } from "./theme-utils.ts";

test("getInitialTheme uses stored light preference", () => {
  assert.equal(
    getInitialTheme({
      storage: { getItem: () => "light" },
      prefersLight: () => false,
    }),
    "light",
  );
});

test("getInitialTheme falls back to system preference", () => {
  assert.equal(
    getInitialTheme({
      storage: { getItem: () => null },
      prefersLight: () => true,
    }),
    "light",
  );
});

test("getThemeColor returns matching browser chrome colors", () => {
  assert.equal(getThemeColor("dark"), "#0d0f17");
  assert.equal(getThemeColor("light"), "#f5f4ef");
});

test("applyTheme updates document theme, storage, and theme-color meta", () => {
  const meta = { content: "" };
  const documentLike = {
    documentElement: { dataset: {} as Record<string, string> },
    querySelector: () => meta,
  };
  const storage = {
    saved: "",
    setItem(_key: string, value: string) {
      this.saved = value;
    },
  };

  applyTheme("light", { document: documentLike, storage });

  assert.equal(documentLike.documentElement.dataset.theme, "light");
  assert.equal(storage.saved, "light");
  assert.equal(meta.content, "#f5f4ef");
});
