import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import type { Todo } from "@/lib/types";

const replace = vi.fn();
vi.mock("next/navigation", () => ({
  useRouter: () => ({ replace, push: vi.fn(), refresh: vi.fn() }),
}));

vi.mock("@/lib/api", async (orig) => {
  const real = await orig<typeof import("@/lib/api")>();
  return {
    ApiError: real.ApiError,
    api: {
      listTodos: vi.fn(),
      createTodo: vi.fn(),
      updateTodo: vi.fn(),
      deleteTodo: vi.fn(),
      logout: vi.fn(),
    },
  };
});

import { ApiError, api } from "@/lib/api";
import { Providers } from "./providers";
import { TodoScreen } from "./todo-screen";

const mk = (id: string, position: number, title = `Task ${id}`): Todo => ({
  id,
  title,
  notes: null,
  is_done: false,
  position,
  due_at: null,
  remind_at: null,
  created_at: "2026-01-01T00:00:00Z",
  updated_at: "2026-01-01T00:00:00Z",
});

function renderScreen() {
  return render(
    <Providers>
      <TodoScreen />
    </Providers>,
  );
}

beforeEach(() => {
  vi.resetAllMocks();
  vi.mocked(api.updateTodo).mockImplementation(async (id, patch) => ({ ...mk(id, 1), ...patch }));
});

describe("TodoScreen", () => {
  it("empty list shows EmptyState", async () => {
    vi.mocked(api.listTodos).mockResolvedValue({ items: [], next_cursor: null });
    renderScreen();
    expect(await screen.findByRole("heading", { name: "Nothing to do yet" })).toBeInTheDocument();
  });

  it("items render after load", async () => {
    vi.mocked(api.listTodos).mockResolvedValue({
      items: [mk("a", 1024, "Buy milk"), mk("b", 2048, "Walk dog")],
      next_cursor: null,
    });
    renderScreen();
    expect(await screen.findByText("Buy milk")).toBeInTheDocument();
    expect(screen.getByText("Walk dog")).toBeInTheDocument();
  });

  it("pressing n focuses New todo input", async () => {
    vi.mocked(api.listTodos).mockResolvedValue({ items: [mk("a", 1024)], next_cursor: null });
    renderScreen();
    await screen.findByText("Task a");
    await userEvent.keyboard("n");
    expect(screen.getByRole("textbox", { name: "New todo" })).toHaveFocus();
    expect(screen.getByRole("textbox", { name: "New todo" })).toHaveValue("");
  });

  it("x toggles selected item", async () => {
    vi.mocked(api.listTodos).mockResolvedValue({
      items: [mk("a", 1024), mk("b", 2048)],
      next_cursor: null,
    });
    renderScreen();
    await screen.findByText("Task a");
    await userEvent.keyboard("j");
    await userEvent.keyboard("x");
    await waitFor(() => expect(api.updateTodo).toHaveBeenCalledWith("a", { is_done: true }));
  });

  it("401 redirects to /login", async () => {
    vi.mocked(api.listTodos).mockRejectedValue(new ApiError(401, "not authenticated"));
    renderScreen();
    await waitFor(() => expect(replace).toHaveBeenCalledWith("/login"));
  });
});
