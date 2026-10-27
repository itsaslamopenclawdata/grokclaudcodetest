/** Colour tokens from PLAN.md "Frontend UX and design direction". Mirrored in app/globals.css. */
export const tokens = {
  light: {
    bg: "#FAFAF9",
    surface: "#FFFFFF",
    fg: "#1C1917",
    muted: "#57534E",
    accent: "#5B4BDB",
    accentFg: "#FFFFFF",
    border: "#E7E5E4",
    success: "#15803D",
    danger: "#B91C1C",
  },
  dark: {
    bg: "#0B0B0F",
    surface: "#16161D",
    fg: "#F5F5F4",
    muted: "#A8A29E",
    accent: "#A59BFF",
    accentFg: "#0B0B0F",
    border: "#2A2A33",
    success: "#4ADE80",
    danger: "#F87171",
  },
} as const;

export type TokenName = keyof typeof tokens.light;

/** [text, background] pairs that must meet WCAG AA (4.5:1). */
export const TEXT_PAIRS: ReadonlyArray<[TokenName, TokenName]> = [
  ["fg", "bg"],
  ["fg", "surface"],
  ["muted", "bg"],
  ["muted", "surface"],
  ["accentFg", "accent"],
  ["accent", "bg"],
  ["success", "surface"],
  ["danger", "surface"],
];
