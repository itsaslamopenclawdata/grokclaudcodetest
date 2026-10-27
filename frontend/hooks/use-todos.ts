"use client";

import {
  type InfiniteData,
  type QueryClient,
  useInfiniteQuery,
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";
import { toast } from "sonner";
import { api } from "@/lib/api";
import type { Todo, TodoCreate, TodoPage, TodoUpdate } from "@/lib/types";

export const todosKey = ["todos"] as const;

type Data = InfiniteData<TodoPage>;
type Ctx = { prev?: Data };

export function flattenTodos(data?: Data): Todo[] {
  if (!data) return [];
  return data.pages.flatMap((p) => p.items).sort((a, b) => a.position - b.position);
}

export function useTodos() {
  return useInfiniteQuery({
    queryKey: todosKey,
    queryFn: ({ pageParam }) => api.listTodos(pageParam),
    initialPageParam: null as string | null,
    getNextPageParam: (p: TodoPage) => p.next_cursor,
  });
}

/** Apply `fn` to every page's items, keeping the page/cursor structure intact. */
function mapItems(data: Data | undefined, fn: (items: Todo[]) => Todo[]): Data | undefined {
  if (!data) return data;
  return { ...data, pages: data.pages.map((p) => ({ ...p, items: fn(p.items) })) };
}

async function snapshot(qc: QueryClient): Promise<Ctx> {
  await qc.cancelQueries({ queryKey: todosKey });
  return { prev: qc.getQueryData<Data>(todosKey) };
}

function rollback(qc: QueryClient, what: string) {
  return (err: Error, _vars: unknown, ctx?: Ctx) => {
    if (ctx?.prev) qc.setQueryData(todosKey, ctx.prev);
    toast.error(`Couldn't ${what}`, { description: err.message });
  };
}

function settle(qc: QueryClient) {
  return () => qc.invalidateQueries({ queryKey: todosKey });
}

export function useCreateTodo() {
  const qc = useQueryClient();
  return useMutation<Todo, Error, TodoCreate, Ctx>({
    mutationFn: (body) => api.createTodo(body),
    onMutate: async (body) => {
      const ctx = await snapshot(qc);
      const now = new Date().toISOString();
      const max = flattenTodos(ctx.prev).reduce((m, t) => Math.max(m, t.position), 0);
      const temp: Todo = {
        id: `tmp-${crypto.randomUUID()}`,
        title: body.title,
        notes: body.notes ?? null,
        is_done: false,
        position: max + 1024,
        due_at: body.due_at ?? null,
        remind_at: body.remind_at ?? null,
        created_at: now,
        updated_at: now,
      };
      if (ctx.prev) {
        const pages = [...ctx.prev.pages];
        const last = pages.length - 1;
        pages[last] = { ...pages[last], items: [...pages[last].items, temp] };
        qc.setQueryData<Data>(todosKey, { ...ctx.prev, pages });
      } else {
        qc.setQueryData<Data>(todosKey, {
          pages: [{ items: [temp], next_cursor: null }],
          pageParams: [null],
        });
      }
      return ctx;
    },
    onError: rollback(qc, "add task"),
    onSettled: settle(qc),
  });
}

export function useUpdateTodo() {
  const qc = useQueryClient();
  return useMutation<Todo, Error, { id: string; patch: TodoUpdate }, Ctx>({
    mutationFn: ({ id, patch }) => api.updateTodo(id, patch),
    onMutate: async ({ id, patch }) => {
      const ctx = await snapshot(qc);
      qc.setQueryData(
        todosKey,
        mapItems(ctx.prev, (items) => items.map((t) => (t.id === id ? { ...t, ...patch } : t))),
      );
      return ctx;
    },
    onError: rollback(qc, "save task"),
    onSettled: settle(qc),
  });
}

export function useDeleteTodo() {
  const qc = useQueryClient();
  return useMutation<void, Error, string, Ctx>({
    mutationFn: (id) => api.deleteTodo(id),
    onMutate: async (id) => {
      const ctx = await snapshot(qc);
      qc.setQueryData(
        todosKey,
        mapItems(ctx.prev, (items) => items.filter((t) => t.id !== id)),
      );
      return ctx;
    },
    onError: rollback(qc, "delete task"),
    onSettled: settle(qc),
  });
}
