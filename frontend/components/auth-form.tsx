"use client";

import { Loader2 } from "lucide-react";
import { useId, useState } from "react";
import { Button } from "@/components/ui/button";
import { ApiError, api } from "@/lib/api";

const MIN_PASSWORD = 8;

const inputClass =
  "h-10 w-full rounded-lg border border-border bg-surface px-3 text-sm text-fg shadow-xs outline-none transition-[border-color,box-shadow] duration-150 placeholder:text-muted focus-visible:border-accent focus-visible:ring-3 focus-visible:ring-accent/25 aria-invalid:border-danger";

export function AuthForm({ onSuccess }: { onSuccess: () => void }) {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);
  const id = useId();
  const isRegister = mode === "register";

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (pending) return;
    if (!email.includes("@")) return setError("Enter a valid email address.");
    if (password.length < MIN_PASSWORD) {
      return setError(`Password must be at least ${MIN_PASSWORD} characters.`);
    }
    setError(null);
    setPending(true);
    try {
      if (isRegister) await api.register(email, password);
      await api.login(email, password);
      onSuccess();
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Something went wrong. Try again.");
    } finally {
      setPending(false);
    }
  }

  return (
    <form noValidate onSubmit={onSubmit} className="flex w-full flex-col gap-5" aria-describedby={error ? `${id}-err` : undefined}>
      <div className="space-y-1">
        <h1 className="text-2xl font-semibold tracking-tight text-fg">
          {isRegister ? "Create your account" : "Welcome back"}
        </h1>
        <p className="text-sm text-muted">
          {isRegister ? "Start keeping track in seconds." : "Sign in to see your tasks."}
        </p>
      </div>

      <div className="space-y-1.5">
        <label htmlFor={`${id}-email`} className="text-sm font-medium text-fg">
          Email
        </label>
        <input
          id={`${id}-email`}
          type="email"
          autoComplete="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className={inputClass}
          placeholder="you@example.com"
        />
      </div>

      <div className="space-y-1.5">
        <label htmlFor={`${id}-password`} className="text-sm font-medium text-fg">
          Password
        </label>
        <input
          id={`${id}-password`}
          type="password"
          autoComplete={isRegister ? "new-password" : "current-password"}
          required
          minLength={MIN_PASSWORD}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          aria-invalid={error !== null && password.length < MIN_PASSWORD}
          className={inputClass}
        />
        <p className="text-xs text-muted">At least {MIN_PASSWORD} characters.</p>
      </div>

      {error && (
        <p
          id={`${id}-err`}
          role="alert"
          className="rounded-lg border border-danger/30 bg-danger/10 px-3 py-2 text-sm text-danger animate-in fade-in-0 slide-in-from-top-1 duration-200 motion-reduce:animate-none"
        >
          {error}
        </p>
      )}

      <Button type="submit" size="lg" disabled={pending} className="h-10 w-full">
        {pending && <Loader2 className="animate-spin motion-reduce:animate-none" aria-hidden />}
        {isRegister ? "Create account" : "Sign in"}
      </Button>

      <p className="text-center text-sm text-muted">
        {isRegister ? "Already registered?" : "New here?"}{" "}
        <button
          type="button"
          onClick={() => {
            setMode(isRegister ? "login" : "register");
            setError(null);
          }}
          className="rounded-sm font-medium text-accent underline-offset-4 outline-none hover:underline focus-visible:ring-3 focus-visible:ring-accent/40"
        >
          {isRegister ? "I have an account" : "Create an account"}
        </button>
      </p>
    </form>
  );
}
