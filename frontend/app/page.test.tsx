import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Page from "./page";

describe("home page", () => {
  it("renders a main landmark", () => {
    render(<Page />);
    expect(screen.getByRole("main")).toBeInTheDocument();
  });

  it("has no element with role alert", () => {
    render(<Page />);
    expect(screen.queryByRole("alert")).toBeNull();
  });
});
