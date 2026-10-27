import { readFileSync } from "node:fs";
import path from "node:path";
import { describe, expect, it } from "vitest";

const css = readFileSync(path.join(process.cwd(), "app/globals.css"), "utf8");
const count = (needle: string) => css.split(needle).length - 1;

describe("globals.css shadcn mapping", () => {
  it("primary maps to accent", () => {
    expect(count("--primary: var(--accent);")).toBe(2);
  });

  it("primary foreground maps to accent-fg", () => {
    expect(count("--primary-foreground: var(--accent-fg);")).toBe(2);
  });

  it("no hard-coded primary colour", () => {
    expect(css).not.toMatch(/--primary:\s*oklch\(/);
  });
});
