import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { AddTodo } from "./add-todo";

describe("AddTodo", () => {
  it("enter submits trimmed title and clears", async () => {
    const onCreate = vi.fn();
    render(<AddTodo onCreate={onCreate} />);
    const input = screen.getByRole("textbox", { name: "New todo" });
    await userEvent.type(input, "  Buy milk  {Enter}");
    expect(onCreate).toHaveBeenCalledWith("Buy milk");
    expect(input).toHaveValue("");
  });

  it("button submits", async () => {
    const onCreate = vi.fn();
    render(<AddTodo onCreate={onCreate} />);
    await userEvent.type(screen.getByRole("textbox", { name: "New todo" }), "Walk");
    await userEvent.click(screen.getByRole("button", { name: "Add" }));
    expect(onCreate).toHaveBeenCalledWith("Walk");
  });

  it("blank title does not submit", async () => {
    const onCreate = vi.fn();
    render(<AddTodo onCreate={onCreate} />);
    await userEvent.type(screen.getByRole("textbox", { name: "New todo" }), "   {Enter}");
    await userEvent.click(screen.getByRole("button", { name: "Add" }));
    expect(onCreate).not.toHaveBeenCalled();
  });
});
