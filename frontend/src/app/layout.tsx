import type { Metadata } from "next";
import Sidebar from "@/components/layout/Sidebar";
import "./globals.css";

export const metadata: Metadata = {
  title: "la soccer Machine | Analytics",
  description: "Plateforme d'analyse tactique professionnelle",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr">
      <body style={{ display: "flex", minHeight: "100vh", overflow: "hidden" }}>
        <Sidebar />
        <main style={{ flex: 1, overflowY: "auto", background: "#080c0a" }}>
          {children}
        </main>
      </body>
    </html>
  );
}
