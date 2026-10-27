import { ListChecks, Plus } from "lucide-react";
import { Button } from "@/components/ui/button";

export function EmptyState({ onAdd }: { onAdd: () => void }) {
  return (
    <div className="flex flex-col items-center gap-4 rounded-2xl border border-dashed border-border px-6 py-14 text-center animate-in fade-in-0 zoom-in-95 duration-250 motion-reduce:animate-none">
      <div className="grid size-12 place-items-center rounded-full bg-accent/10 text-accent">
        <ListChecks className="size-6" aria-hidden="true" />
      </div>
      <div className="space-y-1">
        <h2 className="text-base font-semibold text-fg">Nothing to do yet</h2>
        <p className="text-sm text-muted">
          Press{" "}
          <kbd className="rounded border border-border bg-bg px-1.5 py-0.5 font-mono text-xs text-fg">
            N
          </kbd>{" "}
          to add your first task
        </p>
      </div>
      <Button variant="outline" onClick={onAdd}>
        <Plus aria-hidden="true" />
        Add a task
      </Button>
    </div>
  );
}
