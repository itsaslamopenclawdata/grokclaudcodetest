import { render, screen, within } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import type { Todo } from "@/lib/types";
import { TodoList, handleDragEnd } from "./todo-list";

const mk = (id: string, position: number): Todo => ({
  id,
  title: `Task ${id}`,
  notes: null,
  is_done: false,
  position,
  due_at: null,
  remind_at: null,
  created_at: "2026-01-01T00:00:00Z",
  updated_at: "2026-01-01T00:00:00Z",
});
const todos = [mk("a", 1024), mk("b", 2048), mk("c", 3072)];

describe("TodoList", () => {
  it("renders items in order", () => {
    render(
      <TodoList
        todos={[todos[2], todos[0], todos[1]]}
        selectedId={null}
        onToggle={vi.fn()}
        onDelete={vi.fn()}
        onReorder={vi.fn()}
      />,
    );
    const items = screen.getAllByRole("listitem");
    expect(items.map((li) => within(li).getByText(/Task/).textContent)).toEqual([
      "Task a",
      "Task b",
      "Task c",
    ]);
  });

  it("handleDragEnd moving last to first", () => {
    expect(handleDragEnd(todos, "c", "a")).toEqual({ id: "c", position: 512 });
  });

  it("handleDragEnd same slot returns null", () => {
    expect(handleDragEnd(todos, "b", "b")).toBeNull();
  });

  it("handleDragEnd with null over returns null", () => {
    expect(handleDragEnd(todos, "b", null)).toBeNull();
  });
});
