import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import type { Todo } from "@/lib/types";
import { TodoItem } from "./todo-item";

const base: Todo = {
  id: "t1",
  title: "Buy milk",
  notes: null,
  is_done: false,
  position: 1024,
  due_at: null,
  remind_at: null,
  created_at: "2026-01-01T00:00:00Z",
  updated_at: "2026-01-01T00:00:00Z",
};

function setup(todo: Todo = base) {
  const onToggle = vi.fn();
  const onDelete = vi.fn();
  render(
    <ul>
      <TodoItem todo={todo} onToggle={onToggle} onDelete={onDelete} />
    </ul>,
  );
  return { onToggle, onDelete, user: userEvent.setup() };
}

describe("TodoItem", () => {
  it("toggle calls onToggle(id, true)", async () => {
    const { onToggle, user } = setup();
    await user.click(screen.getByRole("checkbox", { name: 'Mark "Buy milk" done' }));
    expect(onToggle).toHaveBeenCalledWith("t1", true);
  });

  it("delete calls onDelete(id)", async () => {
    const { onDelete, user } = setup();
    await user.click(screen.getByRole("button", { name: 'Delete "Buy milk"' }));
    expect(onDelete).toHaveBeenCalledWith("t1");
  });

  it("done item has line-through class", () => {
    setup({ ...base, is_done: true });
    expect(screen.getByText("Buy milk")).toHaveClass("line-through");
  });

  it("undone item is not checked", () => {
    setup();
    expect(screen.getByRole("checkbox")).toHaveAttribute("aria-checked", "false");
  });
});
