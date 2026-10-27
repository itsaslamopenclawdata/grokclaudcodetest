"use client";

import * as React from "react";
import { Moon, Sun } from "lucide-react";
import { useTheme } from "next-themes";
import { Button } from "@/components/ui/button";

const subscribe = () => () => {};

/** Light/dark switch. Renders nothing until mounted, so SSR markup never mismatches. */
export function ThemeToggle(): React.JSX.Element | null {
  const { resolvedTheme, setTheme } = useTheme();
  const mounted = React.useSyncExternalStore(
    subscribe,
    () => true,
    () => false,
  );
  if (!mounted) return null;

  const isLight = resolvedTheme === "light";
  const label = isLight ? "Switch to dark theme" : "Switch to light theme";
  return (
    <Button
      variant="ghost"
      size="icon"
      aria-label={label}
      title={label}
      onClick={() => setTheme(isLight ? "dark" : "light")}
      className="rounded-full text-muted hover:text-fg"
    >
      <span
        key={isLight ? "moon" : "sun"}
        className="animate-in fade-in-0 spin-in-45 zoom-in-75 duration-200 motion-reduce:animate-none"
      >
        {isLight ? <Moon aria-hidden="true" /> : <Sun aria-hidden="true" />}
      </span>
    </Button>
  );
}
