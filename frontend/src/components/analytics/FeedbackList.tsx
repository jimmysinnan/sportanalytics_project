interface FeedbackItem { text: string; ok: boolean; }
interface Props { items: FeedbackItem[] | string[]; }

export default function FeedbackList({ items }: Props) {
  return (
    <ul style={{ listStyle: "none", padding: 0 }}>
      {items.map((item, i) => {
        const text = typeof item === "string" ? item : item.text;
        const ok = typeof item === "string" ? true : item.ok;
        return (
          <li key={i} style={{
            padding: "8px 0", borderBottom: "1px solid rgba(57,255,106,0.06)",
            fontSize: "0.81rem", color: "#7a9e82", display: "flex", gap: "9px", alignItems: "flex-start",
          }}>
            <span style={{ color: ok ? "#39ff6a" : "#ffa040", flexShrink: 0 }}>{ok ? "✔" : "⚠"}</span>
            <span>{text}</span>
          </li>
        );
      })}
    </ul>
  );
}
