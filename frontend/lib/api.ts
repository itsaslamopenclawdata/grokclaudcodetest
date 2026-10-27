import type { Todo, TodoCreate, TodoPage, TodoUpdate } from "./types";

export class ApiError extends Error {
  constructor(
    public status: number,
    public detail: string,
  ) {
    super(detail);
    this.name = "ApiError";
  }
}

const BASE = "/api/v1";

function detailOf(body: unknown, fallback: string): string {
  if (body && typeof body === "object" && "detail" in body) {
    const d = (body as { detail: unknown }).detail;
    if (typeof d === "string") return d;
    if (Array.isArray(d) && d[0] && typeof d[0] === "object" && "msg" in d[0]) {
      return String((d[0] as { msg: unknown }).msg);
    }
  }
  return fallback;
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  if (init.body !== undefined) headers.set("content-type", "application/json");
  const res = await fetch(`${BASE}${path}`, { ...init, headers, credentials: "include" });
  if (res.status === 204) return undefined as T;
  const text = await res.text();
  const body: unknown = text ? JSON.parse(text) : undefined;
  if (!res.ok) throw new ApiError(res.status, detailOf(body, res.statusText || "request failed"));
  return body as T;
}

const json = (method: string, body: unknown): RequestInit => ({
  method,
  body: JSON.stringify(body),
});

export const api = {
  async register(email: string, password: string): Promise<void> {
    await request("/auth/register", json("POST", { email, password }));
  },
  async login(email: string, password: string): Promise<void> {
    await request("/auth/login", json("POST", { email, password }));
  },
  async logout(): Promise<void> {
    await request("/auth/logout", { method: "POST" });
  },
  listTodos(cursor?: string | null, limit = 50): Promise<TodoPage> {
    const q = new URLSearchParams({ limit: String(limit) });
    if (cursor) q.set("cursor", cursor);
    return request<TodoPage>(`/todos?${q}`);
  },
  createTodo(body: TodoCreate): Promise<Todo> {
    return request<Todo>("/todos", json("POST", body));
  },
  updateTodo(id: string, body: TodoUpdate): Promise<Todo> {
    return request<Todo>(`/todos/${encodeURIComponent(id)}`, json("PATCH", body));
  },
  async deleteTodo(id: string): Promise<void> {
    await request(`/todos/${encodeURIComponent(id)}`, { method: "DELETE" });
  },
};
