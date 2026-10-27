import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { EmptyState } from "./empty-state";

describe("EmptyState", () => {
  it("shows heading level 2", () => {
    render(<EmptyState onAdd={vi.fn()} />);
    expect(screen.getByRole("heading", { level: 2, name: "Nothing to do yet" })).toBeInTheDocument();
    expect(screen.getByText(/to add your first task/i)).toBeInTheDocument();
  });

  it("button calls onAdd", async () => {
    const onAdd = vi.fn();
    render(<EmptyState onAdd={onAdd} />);
    await userEvent.click(screen.getByRole("button", { name: "Add a task" }));
    expect(onAdd).toHaveBeenCalledTimes(1);
  });

  it("icon is hidden from screen readers", () => {
    const { container } = render(<EmptyState onAdd={vi.fn()} />);
    const svgs = container.querySelectorAll("svg");
    expect(svgs.length).toBeGreaterThan(0);
    svgs.forEach((s) => expect(s).toHaveAttribute("aria-hidden", "true"));
  });
});
