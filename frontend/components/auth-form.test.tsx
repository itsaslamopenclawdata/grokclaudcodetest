import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("@/lib/api", async (orig) => {
  const real = await orig<typeof import("@/lib/api")>();
  return {
    ApiError: real.ApiError,
    api: { login: vi.fn(), register: vi.fn() },
  };
});

import { ApiError, api } from "@/lib/api";
import { AuthForm } from "./auth-form";

const login = vi.mocked(api.login);
const register = vi.mocked(api.register);

beforeEach(() => {
  login.mockReset().mockResolvedValue(undefined);
  register.mockReset().mockResolvedValue(undefined);
});

async function fill(email: string, password: string) {
  const user = userEvent.setup();
  await user.type(screen.getByLabelText(/email/i), email);
  await user.type(screen.getByLabelText(/password/i), password);
  return user;
}

describe("AuthForm", () => {
  it("submits login", async () => {
    const onSuccess = vi.fn();
    render(<AuthForm onSuccess={onSuccess} />);
    const user = await fill("a@b.co", "password1");
    await user.click(screen.getByRole("button", { name: "Sign in" }));
    expect(login).toHaveBeenCalledWith("a@b.co", "password1");
    expect(onSuccess).toHaveBeenCalled();
  });

  it("register mode calls register then login", async () => {
    const onSuccess = vi.fn();
    render(<AuthForm onSuccess={onSuccess} />);
    const user = userEvent.setup();
    await user.click(screen.getByRole("button", { name: "Create an account" }));
    await fill("a@b.co", "password1");
    await user.click(screen.getByRole("button", { name: /create account/i }));
    expect(register).toHaveBeenCalledWith("a@b.co", "password1");
    expect(login).toHaveBeenCalledWith("a@b.co", "password1");
    expect(register.mock.invocationCallOrder[0]).toBeLessThan(login.mock.invocationCallOrder[0]);
    expect(onSuccess).toHaveBeenCalled();
  });

  it("shows server error in alert", async () => {
    login.mockRejectedValue(new ApiError(401, "invalid credentials"));
    const onSuccess = vi.fn();
    render(<AuthForm onSuccess={onSuccess} />);
    const user = await fill("a@b.co", "password1");
    await user.click(screen.getByRole("button", { name: "Sign in" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("invalid credentials");
    expect(onSuccess).not.toHaveBeenCalled();
  });

  it("short password blocks submit", async () => {
    render(<AuthForm onSuccess={vi.fn()} />);
    const user = await fill("a@b.co", "12345");
    await user.click(screen.getByRole("button", { name: "Sign in" }));
    expect(login).not.toHaveBeenCalled();
  });
});
