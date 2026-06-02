interface Props {
  title: string;
  badge?: string;
  badgeVariant?: "green" | "cyan";
}

export default function TopBar({ title, badge, badgeVariant = "green" }: Props) {
  const badgeStyle =
    badgeVariant === "cyan"
      ? { background: "rgba(0,229,255,0.08)", border: "1px solid rgba(0,229,255,0.25)", color: "#00e5ff" }
      : { background: "rgba(57,255,106,0.08)", border: "1px solid rgba(57,255,106,0.25)", color: "#39ff6a" };

  return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "24px" }}>
      <h1 className="text-grad" style={{ fontSize: "1.35rem", fontWeight: 700 }}>{title}</h1>
      {badge && (
        <span style={{ ...badgeStyle, fontSize: "0.7rem", padding: "4px 12px", borderRadius: "20px" }}>
          {badge}
        </span>
      )}
    </div>
  );
}
