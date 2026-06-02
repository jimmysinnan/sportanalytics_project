import { ReactNode } from "react";

interface Props { title: string; children: ReactNode; cyan?: boolean; }

export default function CardSection({ title, children, cyan }: Props) {
  return (
    <div style={{
      background: "#111a13", border: "1px solid rgba(57,255,106,0.18)",
      borderRadius: "12px", padding: "20px",
    }}>
      <div style={{
        fontSize: "0.75rem", fontWeight: 700,
        color: cyan ? "#00e5ff" : "#00e5ff",
        letterSpacing: "0.1em", textTransform: "uppercase",
        marginBottom: "16px", display: "flex", alignItems: "center", gap: "8px",
      }}>{title}</div>
      {children}
    </div>
  );
}
