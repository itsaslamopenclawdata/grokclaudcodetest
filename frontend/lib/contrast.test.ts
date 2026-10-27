import { describe, expect, it } from "vitest";
import { contrastRatio } from "./contrast";
import { TEXT_PAIRS, tokens } from "./tokens";

describe("contrastRatio", () => {
  it("black on white is 21", () => {
    expect(contrastRatio("#000000", "#FFFFFF")).toBeCloseTo(21, 2);
  });

  it("every TEXT_PAIR passes AA in light and dark", () => {
    for (const theme of ["light", "dark"] as const) {
      for (const [fg, bg] of TEXT_PAIRS) {
        const ratio = contrastRatio(tokens[theme][fg], tokens[theme][bg]);
        expect(ratio, `${theme} ${fg}/${bg}`).toBeGreaterThanOrEqual(4.5);
      }
    }
  });

  it("low-contrast pair fails", () => {
    expect(contrastRatio("#777777", "#888888")).toBeLessThan(4.5);
  });

  it("invalid hex throws", () => {
    expect(() => contrastRatio("#GG0000", "#FFFFFF")).toThrow("invalid hex");
  });
});
