"use client";

import { X } from "lucide-react";
import { motion, useReducedMotion } from "motion/react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import type { Todo } from "@/lib/types";

const spring = { type: "spring", stiffness: 500, damping: 35 } as const;

export function TodoItem({
  todo,
  selected = false,
  onToggle,
  onDelete,
  dragHandle,
  sortable,
}: {
  todo: Todo;
  selected?: boolean;
  onToggle: (id: string, done: boolean) => void;
  onDelete: (id: string) => void;
  dragHandle?: React.ReactNode;
  /** Wiring from TodoList's useSortable; dnd-kit owns the transform while sorting. */
  sortable?: {
    ref: (el: HTMLElement | null) => void;
    style?: React.CSSProperties;
    dragging?: boolean;
    sorting?: boolean;
  };
}) {
  const reduce = useReducedMotion() ?? false;
  const done = todo.is_done;
  const pending = todo.id.startsWith("tmp-");

  return (
    <motion.li
      ref={sortable?.ref}
      style={sortable?.style}
      layout={reduce || sortable?.sorting ? false : "position"}
      initial={reduce ? false : { opacity: 0, y: -4 }}
      animate={{ opacity: 1, y: 0 }}
      exit={reduce ? { opacity: 0, transition: { duration: 0 } } : { opacity: 0, x: -12 }}
      transition={reduce ? { duration: 0 } : { ...spring, opacity: { duration: 0.15 } }}
      aria-selected={selected}
      data-id={todo.id}
      className={cn(
        "group relative flex min-h-12 items-center gap-3 rounded-xl px-3 py-2 transition-colors duration-150",
        "hover:bg-foreground/[0.03]",
        selected && "bg-accent/[0.07] ring-1 ring-accent/30",
        pending && "opacity-70",
        sortable?.dragging && "z-10 bg-surface shadow-lg ring-1 ring-border",
      )}
    >
      {dragHandle}
      <motion.button
        type="button"
        role="checkbox"
        aria-checked={done}
        aria-label={`Mark "${todo.title}" done`}
        onClick={() => onToggle(todo.id, !done)}
        whileTap={reduce ? undefined : { scale: 0.85 }}
        transition={spring}
        className={cn(
          "grid size-5 shrink-0 place-items-center rounded-md border-[1.5px] outline-none transition-colors duration-200",
          "focus-visible:ring-2 focus-visible:ring-[var(--accent)] focus-visible:ring-offset-2 focus-visible:ring-offset-bg",
          done ? "border-success bg-success text-white" : "border-border bg-surface hover:border-accent",
        )}
      >
        <svg viewBox="0 0 16 16" className="size-3.5" fill="none" aria-hidden>
          <motion.path
            d="M3.5 8.5 6.5 11.5 12.5 4.5"
            stroke="currentColor"
            strokeWidth={2.25}
            strokeLinecap="round"
            strokeLinejoin="round"
            initial={false}
            animate={{ pathLength: done ? 1 : 0, opacity: done ? 1 : 0 }}
            transition={reduce ? { duration: 0 } : { duration: 0.2, ease: "easeOut" }}
          />
        </svg>
      </motion.button>

      <span
        className={cn(
          "min-w-0 flex-1 truncate text-[15px] leading-6 transition-[color,text-decoration-color] duration-200",
          done ? "text-muted line-through decoration-muted/70" : "text-fg decoration-transparent",
        )}
        title={todo.title}
      >
        {todo.title}
      </span>

      <Button
        variant="ghost"
        size="icon-sm"
        aria-label={`Delete "${todo.title}"`}
        onClick={() => onDelete(todo.id)}
        className="text-muted opacity-0 transition-opacity duration-150 group-hover:opacity-100 group-focus-within:opacity-100 hover:text-danger focus-visible:opacity-100 focus-visible:ring-2 focus-visible:ring-[var(--accent)] [li[aria-selected=true]_&]:opacity-100 pointer-coarse:opacity-100"
      >
        <X aria-hidden />
      </Button>
    </motion.li>
  );
}
