import { render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it } from "vitest";
import { ThemeProvider } from "./theme-provider";

beforeEach(() => {
  localStorage.clear();
  document.documentElement.className = "";
});

describe("ThemeProvider", () => {
  it("renders children", () => {
    render(
      <ThemeProvider attribute="class" defaultTheme="light">
        <p>hi</p>
      </ThemeProvider>,
    );
    expect(screen.getByText("hi")).toBeInTheDocument();
  });

  it("applies dark class from defaultTheme", async () => {
    render(
      <ThemeProvider attribute="class" defaultTheme="dark">
        <p>hi</p>
      </ThemeProvider>,
    );
    await waitFor(() => expect(document.documentElement.classList.contains("dark")).toBe(true));
  });

  it("light theme has no dark class", async () => {
    render(
      <ThemeProvider attribute="class" defaultTheme="light">
        <p>hi</p>
      </ThemeProvider>,
    );
    await waitFor(() => expect(document.documentElement.classList.contains("light")).toBe(true));
    expect(document.documentElement.classList.contains("dark")).toBe(false);
  });
});
