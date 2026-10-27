import { describe, expect, it } from "vitest";
import { STEP, positionBetween, positionForMove } from "./position";

describe("positionBetween", () => {
  it("empty list gives STEP", () => expect(positionBetween(null, null)).toBe(STEP));
  it("top gives half", () => expect(positionBetween(null, 1024)).toBe(512));
  it("bottom adds STEP", () => expect(positionBetween(2048, null)).toBe(2048 + STEP));
  it("middle gives midpoint", () => expect(positionBetween(1024, 2048)).toBe(1536));
  it("positionForMove moves index 2 to 0", () =>
    expect(positionForMove([1024, 2048, 3072], 2, 0)).toBe(512));
  it("before >= after throws", () => {
    expect(() => positionBetween(2048, 1024)).toThrow(RangeError);
    expect(() => positionBetween(1024, 1024)).toThrow(RangeError);
  });
});
