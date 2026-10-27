import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { SHORTCUTS, ShortcutsDialog } from "./shortcuts-dialog";

describe("ShortcutsDialog", () => {
  it("open shows dialog titled Keyboard shortcuts", () => {
    render(<ShortcutsDialog open onOpenChange={vi.fn()} />);
    expect(screen.getByRole("dialog", { name: "Keyboard shortcuts" })).toBeInTheDocument();
  });

  it("lists 6 shortcuts", () => {
    render(<ShortcutsDialog open onOpenChange={vi.fn()} />);
    expect(SHORTCUTS).toHaveLength(6);
    const dialog = screen.getByRole("dialog");
    const rows = dialog.querySelectorAll("[data-shortcut]");
    expect(rows).toHaveLength(6);
    rows.forEach((r) => expect(r.querySelector("kbd")).not.toBeNull());
  });

  it("closed renders no dialog", () => {
    render(<ShortcutsDialog open={false} onOpenChange={vi.fn()} />);
    expect(screen.queryByRole("dialog")).toBeNull();
  });
});
