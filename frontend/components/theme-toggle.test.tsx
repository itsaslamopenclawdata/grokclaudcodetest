import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it } from "vitest";
import { ThemeProvider } from "./theme-provider";
import { ThemeToggle } from "./theme-toggle";

function renderToggle() {
  return render(
    <ThemeProvider attribute="class" defaultTheme="light">
      <ThemeToggle />
    </ThemeProvider>,
  );
}

beforeEach(() => {
  localStorage.clear();
  document.documentElement.className = "";
});

describe("ThemeToggle", () => {
  it("label offers dark in light mode", async () => {
    renderToggle();
    expect(await screen.findByRole("button", { name: "Switch to dark theme" })).toBeInTheDocument();
  });

  it("click switches to dark", async () => {
    renderToggle();
    await userEvent.click(await screen.findByRole("button", { name: "Switch to dark theme" }));
    await waitFor(() => {
      expect(document.documentElement.classList.contains("dark")).toBe(true);
      expect(screen.getByRole("button", { name: "Switch to light theme" })).toBeInTheDocument();
    });
  });

  it("no unlabeled button", async () => {
    renderToggle();
    await screen.findByRole("button");
    for (const b of screen.getAllByRole("button")) {
      expect(b).toHaveAccessibleName(/\S/);
    }
  });
});
