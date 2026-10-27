"use client";

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

export const SHORTCUTS: ReadonlyArray<{ keys: string; action: string }> = [
  { keys: "N", action: "New task" },
  { keys: "J / K", action: "Select next / previous" },
  { keys: "X", action: "Toggle done" },
  { keys: "Delete / Backspace", action: "Delete selected" },
  { keys: "?", action: "Show this help" },
  { keys: "Esc", action: "Close dialog or leave input" },
];

function Keys({ keys }: { keys: string }) {
  return (
    <span className="flex items-center gap-1">
      {keys.split(" / ").map((k, i) => (
        <span key={k} className="flex items-center gap-1">
          {i > 0 && <span className="text-xs text-muted">or</span>}
          <kbd className="inline-flex h-6 min-w-6 items-center justify-center rounded-md border border-border border-b-2 bg-bg px-1.5 font-mono text-xs font-medium text-fg">
            {k}
          </kbd>
        </span>
      ))}
    </span>
  );
}

export function ShortcutsDialog({
  open,
  onOpenChange,
}: {
  open: boolean;
  onOpenChange(o: boolean): void;
}) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-sm">
        <DialogHeader>
          <DialogTitle>Keyboard shortcuts</DialogTitle>
          <DialogDescription>Work through your list without touching the mouse.</DialogDescription>
        </DialogHeader>
        <ul className="-mx-1 divide-y divide-border">
          {SHORTCUTS.map((s) => (
            <li
              key={s.keys}
              data-shortcut
              className="flex items-center justify-between gap-4 px-1 py-2.5 text-sm"
            >
              <span className="text-fg">{s.action}</span>
              <Keys keys={s.keys} />
            </li>
          ))}
        </ul>
      </DialogContent>
    </Dialog>
  );
}
