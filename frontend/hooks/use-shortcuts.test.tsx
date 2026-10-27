import { fireEvent, render, renderHook } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { isTypingTarget, useShortcuts } from "./use-shortcuts";

const press = (key: string, init: KeyboardEventInit = {}, target: EventTarget = window) =>
  fireEvent.keyDown(target, { key, bubbles: true, ...init });

describe("useShortcuts", () => {
  it("n fires handler", () => {
    const n = vi.fn();
    renderHook(() => useShortcuts({ n }));
    press("n");
    expect(n).toHaveBeenCalledTimes(1);
  });

  it("? fires handler", () => {
    const help = vi.fn();
    renderHook(() => useShortcuts({ "?": help }));
    press("?", { shiftKey: true });
    expect(help).toHaveBeenCalledTimes(1);
  });

  it("ignored inside input", () => {
    const n = vi.fn();
    renderHook(() => useShortcuts({ n }));
    const { getByRole } = render(<input aria-label="x" />);
    const input = getByRole("textbox");
    input.focus();
    press("n", {}, input);
    expect(n).not.toHaveBeenCalled();
    expect(isTypingTarget(input)).toBe(true);
  });

  it("ignored with ctrl", () => {
    const n = vi.fn();
    renderHook(() => useShortcuts({ n }));
    press("n", { ctrlKey: true });
    press("n", { metaKey: true });
    press("n", { altKey: true });
    expect(n).not.toHaveBeenCalled();
  });

  it("listener removed on unmount", () => {
    const n = vi.fn();
    const { unmount } = renderHook(() => useShortcuts({ n }));
    unmount();
    press("n");
    expect(n).not.toHaveBeenCalled();
  });
});
