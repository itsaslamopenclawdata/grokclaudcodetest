/** Mirrors backend/app/schemas/todo.py and auth.py. Datetimes are ISO 8601 strings. */
export type Todo = {
  id: string;
  title: string;
  notes: string | null;
  is_done: boolean;
  position: number;
  due_at: string | null;
  remind_at: string | null;
  created_at: string;
  updated_at: string;
};

export type TodoPage = { items: Todo[]; next_cursor: string | null };

export type TodoCreate = {
  title: string;
  notes?: string | null;
  due_at?: string | null;
  remind_at?: string | null;
};

export type TodoUpdate = Partial<
  Pick<Todo, "title" | "notes" | "is_done" | "position" | "due_at" | "remind_at">
>;
