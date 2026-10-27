"use client";

import { Plus } from "lucide-react";
import { forwardRef, useState } from "react";
import { Button } from "@/components/ui/button";

export const AddTodo = forwardRef<HTMLInputElement, { onCreate: (title: string) => void }>(
  function AddTodo({ onCreate }, ref) {
    const [title, setTitle] = useState("");

    function submit(e: React.FormEvent) {
      e.preventDefault();
      const t = title.trim();
      if (!t) return;
      onCreate(t);
      setTitle("");
    }

    return (
      <form
        onSubmit={submit}
        className="flex items-center gap-2 rounded-xl border border-border bg-surface p-1.5 pl-3 shadow-xs transition-[border-color,box-shadow] duration-150 focus-within:border-accent focus-within:ring-3 focus-within:ring-accent/20"
      >
        <Plus className="size-4 shrink-0 text-muted" aria-hidden />
        <input
          ref={ref}
          aria-label="New todo"
          placeholder="What needs doing?"
          maxLength={200}
          autoComplete="off"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Escape") e.currentTarget.blur();
          }}
          className="h-9 min-w-0 flex-1 bg-transparent text-[15px] text-fg outline-none placeholder:text-muted"
        />
        <Button type="submit" size="sm" disabled={!title.trim()} className="h-8 px-3">
          Add
        </Button>
      </form>
    );
  },
);
