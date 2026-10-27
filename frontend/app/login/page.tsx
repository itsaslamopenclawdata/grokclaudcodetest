"use client";

import { useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { AuthForm } from "@/components/auth-form";

export default function LoginPage() {
  const router = useRouter();
  const qc = useQueryClient();
  return (
    <main className="flex flex-1 items-center justify-center px-4 py-16">
      <div className="w-full max-w-sm rounded-2xl border border-border bg-surface p-8 shadow-sm">
        <AuthForm
          onSuccess={() => {
            qc.clear();
            router.replace("/");
          }}
        />
      </div>
    </main>
  );
}
