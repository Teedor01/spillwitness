import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "SpillWitness — Same incident. Different records.",
  description:
    "An auditable evidence record for environmental incidents: what conflicting sources actually establish, and what they don't.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-paper font-sans text-ink antialiased">{children}</body>
    </html>
  );
}
