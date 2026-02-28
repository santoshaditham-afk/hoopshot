"use client";
import LoginForm from "@/components/LoginForm";

export default function HomePage() {
  return (
    <main style={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: "100vh" }}>
      <LoginForm />
    </main>
  );
}
