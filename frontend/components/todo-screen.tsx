"use client";

import { useQueryClient } from "@tanstack/react-query";
import { Keyboard, LogOut } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect, useMemo, useRef, useState } from "react";
import { toast } from "sonner";
import { AddTodo } from "@/components/add-todo";
import { EmptyState } from "@/components/empty-state";
import { ShortcutsDialog } from "@/components/shortcuts-dialog";
import { ThemeToggle } from "@/components/theme-toggle";
import { TodoList } from "@/components/todo-list";
import { Button } from "@/components/ui/button";
import {
  flattenTodos,
  useCreateTodo,
  useDeleteTodo,
  useTodos,
  useUpdateTodo,
} from "@/hooks/use-todos";
import { useShortcuts } from "@/hooks/use-shortcuts";
import { ApiError, api } from "@/lib/api";
import type { Todo } from "@/lib/types";

function Skeleton() {
  return (
    <ul aria-hidden className="flex flex-col gap-0.5">
      {[72, 56, 64].map((w) => (
        <li key={w} className="flex h-12 items-center gap-3 px-3">
          <span className="size-5 rounded-md bg-foreground/[0.06] motion-safe:animate-pulse" />
          <span
            className="h-3.5 rounded-full bg-foreground/[0.06] motion-safe:animate-pulse"
            style={{ width: `${w}%` }}
          />
        </li>
      ))}
    </ul>
  );
}

export function TodoScreen() {
  const router = useRouter();
  const qc = useQueryClient();
  const query = useTodos();
  const create = useCreateTodo();
  const update = useUpdateTodo();
  const remove = useDeleteTodo();
  const inputRef = useRef<HTMLInputElement>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [helpOpen, setHelpOpen] = useState(false);

  const todos = useMemo(() => flattenTodos(query.data), [query.data]);
  const remaining = todos.filter((t) => !t.is_done).length;
  const selected = todos.find((t) => t.id === selectedId) ?? null;

  const unauthorized = query.error instanceof ApiError && query.error.status === 401;
  useEffect(() => {
    if (unauthorized) router.replace("/login");
  }, [unauthorized, router]);

  function toggle(id: string, done: boolean) {
    update.mutate({ id, patch: { is_done: done } });
  }

  function del(todo: Todo) {
    const sorted = todos;
    const i = sorted.findIndex((t) => t.id === todo.id);
    const next = sorted[i + 1] ?? sorted[i - 1] ?? null;
    if (selectedId === todo.id) setSelectedId(next?.id ?? null);
    remove.mutate(todo.id, {
      onSuccess: () => {
        toast("Task deleted", {
          description: todo.title,
          duration: 5000,
          action: {
            label: "Undo",
            onClick: () =>
              create.mutate(
                {
                  title: todo.title,
                  notes: todo.notes,
                  due_at: todo.due_at,
                  remind_at: todo.remind_at,
                },
                {
                  onSuccess: (created) =>
                    update.mutate({
                      id: created.id,
                      patch: { position: todo.position, is_done: todo.is_done },
                    }),
                },
              ),
          },
        });
      },
    });
  }

  function move(delta: 1 | -1) {
    if (todos.length === 0) return;
    const i = todos.findIndex((t) => t.id === selectedId);
    const nextIndex =
      i < 0 ? (delta === 1 ? 0 : todos.length - 1) : Math.min(Math.max(i + delta, 0), todos.length - 1);
    const id = todos[nextIndex].id;
    setSelectedId(id);
    document.querySelector(`[data-id="${CSS.escape(id)}"]`)?.scrollIntoView?.({ block: "nearest" });
  }

  useShortcuts({
    n: () => inputRef.current?.focus(),
    j: () => move(1),
    k: () => move(-1),
    x: () => selected && toggle(selected.id, !selected.is_done),
    Delete: () => selected && del(selected),
    Backspace: () => selected && del(selected),
    "?": () => setHelpOpen(true),
  });

  async function logout() {
    try {
      await api.logout();
    } finally {
      qc.clear();
      router.replace("/login");
    }
  }

  const showError = query.isError && !unauthorized;

  return (
    <main className="mx-auto flex w-full max-w-[640px] flex-1 flex-col px-4 pt-10 pb-24 sm:pt-16">
      <header className="mb-6 flex items-center gap-2">
        <div className="min-w-0 flex-1">
          <h1 className="text-2xl font-semibold tracking-tight text-fg">Today</h1>
          <p className="text-sm text-muted tabular-nums" aria-live="polite">
            {query.isPending
              ? "Loading…"
              : remaining === 0
                ? todos.length === 0
                  ? "A clean slate."
                  : "All done. Nice."
                : `${remaining} ${remaining === 1 ? "task" : "tasks"} left`}
          </p>
        </div>
        <Button
          variant="ghost"
          size="icon"
          aria-label="Keyboard shortcuts"
          title="Keyboard shortcuts (?)"
          onClick={() => setHelpOpen(true)}
          className="rounded-full text-muted hover:text-fg"
        >
          <Keyboard aria-hidden />
        </Button>
        <ThemeToggle />
        <Button
          variant="ghost"
          size="icon"
          aria-label="Log out"
          title="Log out"
          onClick={logout}
          className="rounded-full text-muted hover:text-fg"
        >
          <LogOut aria-hidden />
        </Button>
      </header>

      <AddTodo ref={inputRef} onCreate={(title) => create.mutate({ title })} />

      <section aria-label="Tasks" className="mt-4">
        {showError && (
          <div
            role="alert"
            className="flex items-center justify-between gap-3 rounded-xl border border-danger/30 bg-danger/10 px-4 py-3 text-sm text-danger"
          >
            <span>Couldn&apos;t load your tasks. {query.error.message}</span>
            <Button size="sm" variant="outline" onClick={() => query.refetch()}>
              Retry
            </Button>
          </div>
        )}
        {query.isPending && <Skeleton />}
        {query.isSuccess && todos.length === 0 && (
          <EmptyState onAdd={() => inputRef.current?.focus()} />
        )}
        {todos.length > 0 && (
          <TodoList
            todos={todos}
            selectedId={selectedId}
            onToggle={toggle}
            onDelete={(id) => {
              const t = todos.find((x) => x.id === id);
              if (t) del(t);
            }}
            onReorder={(id, position) => update.mutate({ id, patch: { position } })}
          />
        )}
        {query.hasNextPage && (
          <div className="mt-4 flex justify-center">
            <Button
              variant="ghost"
              onClick={() => query.fetchNextPage()}
              disabled={query.isFetchingNextPage}
              className="text-muted hover:text-fg"
            >
              {query.isFetchingNextPage ? "Loading…" : "Load more"}
            </Button>
          </div>
        )}
      </section>

      {todos.length > 0 && (
        <p className="mt-10 hidden text-center text-xs text-muted sm:block">
          Press <kbd className="font-mono">?</kbd> for keyboard shortcuts
        </p>
      )}

      <ShortcutsDialog open={helpOpen} onOpenChange={setHelpOpen} />
    </main>
  );
}
