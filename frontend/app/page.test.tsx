import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ replace: vi.fn(), push: vi.fn(), refresh: vi.fn() }),
}));
vi.mock("@/lib/api", () => ({
  ApiError: class extends Error {},
  api: { listTodos: vi.fn().mockResolvedValue({ items: [], next_cursor: null }) },
}));

import { Providers } from "@/components/providers";
import Page from "./page";

const renderPage = () =>
  render(
    <Providers>
      <Page />
    </Providers>,
  );

describe("home page", () => {
  it("renders a main landmark", () => {
    renderPage();
    expect(screen.getByRole("main")).toBeInTheDocument();
  });

  it("has no element with role alert", () => {
    renderPage();
    expect(screen.queryByRole("alert")).toBeNull();
  });
});
