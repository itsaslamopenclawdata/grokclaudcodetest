/** Spacing between appended items; matches the backend's max+1024 rule. */
export const STEP = 1024;

export function positionBetween(before: number | null, after: number | null): number {
  if (before === null && after === null) return STEP;
  if (before === null) return (after as number) / 2;
  if (after === null) return before + STEP;
  if (before >= after) throw new RangeError(`before (${before}) must be < after (${after})`);
  return (before + after) / 2;
}

/** New position for the item at `from` once it is dropped at index `to` of `sorted`. */
export function positionForMove(sorted: number[], from: number, to: number): number {
  const rest = sorted.filter((_, i) => i !== from);
  return positionBetween(rest[to - 1] ?? null, rest[to] ?? null);
}
