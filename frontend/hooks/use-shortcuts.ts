"use client";

import { useEffect, useRef } from "react";

export type ShortcutMap = Partial<
  Record<"n" | "j" | "k" | "x" | "Delete" | "Backspace" | "?", () => void>
>;

export function isTypingTarget(t: EventTarget | null): boolean {
  if (!(t instanceof HTMLElement)) return false;
  if (t.isContentEditable || t.closest("[contenteditable=''],[contenteditable='true']")) return true;
  const tag = t.tagName;
  return tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT";
}

export function useShortcuts(map: ShortcutMap): void {
  const ref = useRef(map);
  useEffect(() => {
    ref.current = map;
  });

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (e.defaultPrevented || e.ctrlKey || e.metaKey || e.altKey) return;
      if (isTypingTarget(e.target)) return;
      const key = (e.key.length === 1 ? e.key.toLowerCase() : e.key) as keyof ShortcutMap;
      const fn = ref.current[key === "?" ? "?" : key];
      if (!fn) return;
      e.preventDefault();
      fn();
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);
}
