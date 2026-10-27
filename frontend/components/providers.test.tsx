import { render, screen } from "@testing-library/react";
import { useQueryClient } from "@tanstack/react-query";
import { describe, expect, it, vi } from "vitest";
import { Providers } from "./providers";

function UsesClient() {
  useQueryClient();
  return <p>ok</p>;
}

describe("Providers", () => {
  it("children render", () => {
    render(<Providers><p>hello</p></Providers>);
    expect(screen.getByText("hello")).toBeInTheDocument();
  });

  it("useQueryClient works inside", () => {
    render(<Providers><UsesClient /></Providers>);
    expect(screen.getByText("ok")).toBeInTheDocument();
  });

  it("useQueryClient throws outside", () => {
    const spy = vi.spyOn(console, "error").mockImplementation(() => {});
    expect(() => render(<UsesClient />)).toThrow();
    spy.mockRestore();
  });
});
