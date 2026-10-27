import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { ApiError, api } from "./api";

const fetchMock = vi.fn();

function reply(status: number, body?: unknown) {
  return new Response(body === undefined ? null : JSON.stringify(body), {
    status,
    headers: body === undefined ? {} : { "content-type": "application/json" },
  });
}

beforeEach(() => {
  fetchMock.mockReset();
  vi.stubGlobal("fetch", fetchMock);
});
afterEach(() => vi.unstubAllGlobals());

describe("api", () => {
  it("listTodos builds query", async () => {
    fetchMock.mockResolvedValue(reply(200, { items: [], next_cursor: null }));
    await api.listTodos();
    const [url, init] = fetchMock.mock.calls[0];
    expect(url).toBe("/api/v1/todos?limit=50");
    expect(init.credentials).toBe("include");
  });

  it("createTodo posts JSON", async () => {
    fetchMock.mockResolvedValue(reply(201, { id: "1", title: "a" }));
    await api.createTodo({ title: "a" });
    const [url, init] = fetchMock.mock.calls[0];
    expect(url).toBe("/api/v1/todos");
    expect(init.method).toBe("POST");
    expect(new Headers(init.headers).get("content-type")).toBe("application/json");
    expect(JSON.parse(init.body)).toEqual({ title: "a" });
  });

  it("non-2xx throws ApiError with detail", async () => {
    fetchMock.mockResolvedValue(reply(409, { detail: "email already registered" }));
    const err = await api.register("a@b.co", "password1").catch((e: unknown) => e);
    expect(err).toBeInstanceOf(ApiError);
    expect((err as ApiError).status).toBe(409);
    expect((err as ApiError).detail).toBe("email already registered");
  });

  it("deleteTodo resolves on 204", async () => {
    fetchMock.mockResolvedValue(reply(204));
    await expect(api.deleteTodo("abc")).resolves.toBeUndefined();
    expect(fetchMock.mock.calls[0][1].method).toBe("DELETE");
  });
});
