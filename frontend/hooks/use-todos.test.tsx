import { QueryClient, QueryClientProvider, type InfiniteData } from "@tanstack/react-query";
import { act, renderHook, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import type { Todo, TodoPage } from "@/lib/types";

vi.mock("@/lib/api", () => ({
  ApiError: class extends Error {},
  api: {
    listTodos: vi.fn(),
    createTodo: vi.fn(),
    updateTodo: vi.fn(),
    deleteTodo: vi.fn(),
  },
}));

import { api } from "@/lib/api";
import {
  flattenTodos,
  todosKey,
  useCreateTodo,
  useDeleteTodo,
  useUpdateTodo,
} from "./use-todos";

function todo(id: string, position: number, over: Partial<Todo> = {}): Todo {
  return {
    id,
    title: `t${id}`,
    notes: null,
    is_done: false,
    position,
    due_at: null,
    remind_at: null,
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
    ...over,
  };
}

function seed(items: Todo[]): InfiniteData<TodoPage> {
  return { pages: [{ items, next_cursor: null }], pageParams: [null] };
}

let qc: QueryClient;
const wrapper = ({ children }: { children: React.ReactNode }) => (
  <QueryClientProvider client={qc}>{children}</QueryClientProvider>
);
const cached = () => flattenTodos(qc.getQueryData<InfiniteData<TodoPage>>(todosKey));
const never = () => new Promise<never>(() => {});

beforeEach(() => {
  vi.resetAllMocks();
  qc = new QueryClient({ defaultOptions: { queries: { retry: false, staleTime: Infinity } } });
  qc.setQueryData(todosKey, seed([todo("1", 1024)]));
  vi.mocked(api.listTodos).mockImplementation(never);
});

describe("todo hooks", () => {
  it("create shows item before server responds", async () => {
    vi.mocked(api.createTodo).mockImplementation(never);
    const { result } = renderHook(() => useCreateTodo(), { wrapper });
    act(() => result.current.mutate({ title: "fresh" }));
    await waitFor(() => expect(cached().map((t) => t.title)).toContain("fresh"));
    expect(cached().find((t) => t.title === "fresh")?.id).toMatch(/^tmp-/);
  });

  it("update toggles is_done optimistically", async () => {
    vi.mocked(api.updateTodo).mockImplementation(never);
    const { result } = renderHook(() => useUpdateTodo(), { wrapper });
    act(() => result.current.mutate({ id: "1", patch: { is_done: true } }));
    await waitFor(() => expect(cached()[0].is_done).toBe(true));
  });

  it("delete removes optimistically", async () => {
    vi.mocked(api.deleteTodo).mockImplementation(never);
    const { result } = renderHook(() => useDeleteTodo(), { wrapper });
    act(() => result.current.mutate("1"));
    await waitFor(() => expect(cached()).toHaveLength(0));
  });

  it("failed update rolls back", async () => {
    vi.mocked(api.updateTodo).mockRejectedValue(new Error("boom"));
    const { result } = renderHook(() => useUpdateTodo(), { wrapper });
    act(() => result.current.mutate({ id: "1", patch: { is_done: true } }));
    await waitFor(() => expect(result.current.isError).toBe(true));
    expect(cached()[0].is_done).toBe(false);
  });

  it("flattenTodos sorts by position", () => {
    const data: InfiniteData<TodoPage> = {
      pages: [
        { items: [todo("b", 3000), todo("a", 1000)], next_cursor: "x" },
        { items: [todo("c", 2000)], next_cursor: null },
      ],
      pageParams: [null, "x"],
    };
    expect(flattenTodos(data).map((t) => t.id)).toEqual(["a", "c", "b"]);
    expect(flattenTodos(undefined)).toEqual([]);
  });
});
