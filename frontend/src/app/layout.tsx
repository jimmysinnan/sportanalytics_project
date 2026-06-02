import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "La Soccer Machine",
  description: "Plateforme analytics football pro",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="fr" className="h-full">
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}
