"use client";

import {
  DndContext,
  type DragEndEvent,
  KeyboardSensor,
  PointerSensor,
  closestCenter,
  useSensor,
  useSensors,
} from "@dnd-kit/core";
import { restrictToVerticalAxis } from "@dnd-kit/modifiers";
import {
  SortableContext,
  sortableKeyboardCoordinates,
  useSortable,
  verticalListSortingStrategy,
} from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { GripVertical } from "lucide-react";
import { AnimatePresence } from "motion/react";
import { useMemo } from "react";
import { TodoItem } from "@/components/todo-item";
import { positionForMove } from "@/lib/position";
import type { Todo } from "@/lib/types";

const byPosition = (todos: Todo[]) => [...todos].sort((a, b) => a.position - b.position);

export function handleDragEnd(
  todos: Todo[],
  activeId: string,
  overId: string | null,
): { id: string; position: number } | null {
  if (overId === null || overId === activeId) return null;
  const sorted = byPosition(todos);
  const from = sorted.findIndex((t) => t.id === activeId);
  const to = sorted.findIndex((t) => t.id === overId);
  if (from < 0 || to < 0) return null;
  return { id: activeId, position: positionForMove(sorted.map((t) => t.position), from, to) };
}

type Props = {
  todos: Todo[];
  selectedId: string | null;
  onToggle(id: string, done: boolean): void;
  onDelete(id: string): void;
  onReorder(id: string, position: number): void;
};

function SortableTodo({ todo, ...rest }: Omit<Props, "todos" | "selectedId" | "onReorder"> & {
  todo: Todo;
  selected: boolean;
}) {
  const {
    attributes,
    listeners,
    setNodeRef,
    setActivatorNodeRef,
    transform,
    transition,
    isDragging,
    isSorting,
  } = useSortable({ id: todo.id, disabled: todo.id.startsWith("tmp-") });
  return (
    <TodoItem
      todo={todo}
      {...rest}
      sortable={{
        ref: setNodeRef,
        style: { transform: CSS.Translate.toString(transform), transition: transition },
        dragging: isDragging,
        sorting: isSorting,
      }}
      dragHandle={
        <button
          type="button"
          ref={setActivatorNodeRef}
          aria-label={`Reorder "${todo.title}"`}
          className="-ml-1 grid h-8 w-5 shrink-0 cursor-grab touch-none place-items-center rounded-md text-muted/60 opacity-0 outline-none transition-opacity duration-150 group-hover:opacity-100 focus-visible:opacity-100 focus-visible:ring-2 focus-visible:ring-[var(--accent)] active:cursor-grabbing pointer-coarse:opacity-100"
          {...attributes}
          {...listeners}
        >
          <GripVertical className="size-4" aria-hidden />
        </button>
      }
    />
  );
}

export function TodoList({ todos, selectedId, onToggle, onDelete, onReorder }: Props) {
  const sorted = useMemo(() => byPosition(todos), [todos]);
  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 5 } }),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates }),
  );

  function onDragEnd(e: DragEndEvent) {
    const r = handleDragEnd(sorted, String(e.active.id), e.over ? String(e.over.id) : null);
    if (r) onReorder(r.id, r.position);
  }

  return (
    <DndContext
      sensors={sensors}
      collisionDetection={closestCenter}
      modifiers={[restrictToVerticalAxis]}
      onDragEnd={onDragEnd}
    >
      <SortableContext items={sorted.map((t) => t.id)} strategy={verticalListSortingStrategy}>
        <ul aria-label="Todos" className="flex flex-col gap-0.5">
          <AnimatePresence initial={false}>
            {sorted.map((t) => (
              <SortableTodo
                key={t.id}
                todo={t}
                selected={t.id === selectedId}
                onToggle={onToggle}
                onDelete={onDelete}
              />
            ))}
          </AnimatePresence>
        </ul>
      </SortableContext>
    </DndContext>
  );
}
