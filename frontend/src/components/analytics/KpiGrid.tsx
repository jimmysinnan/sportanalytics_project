import KpiCard from "./KpiCard";

export interface KpiItem {
  label: string;
  value: string | number;
  delta?: string;
  deltaUp?: boolean;
  deltaCyan?: boolean;
}

interface Props { kpis: KpiItem[]; cols?: number; }

export default function KpiGrid({ kpis, cols = 4 }: Props) {
  return (
    <div style={{ display: "grid", gridTemplateColumns: `repeat(${cols}, 1fr)`, gap: "14px", marginBottom: "22px" }}>
      {kpis.map(k => <KpiCard key={k.label} {...k} />)}
    </div>
  );
}
