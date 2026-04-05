import { cn } from "../lib/utils";
import type { BackendStatus, PlanKind } from "../types/api";

type StatusChipProps = {
  label: string;
  value: string;
  tone?: "default" | "success" | "warning" | "danger" | PlanKind | BackendStatus;
};

const toneStyles: Record<string, string> = {
  default: "border-slate/15 bg-slate/10 text-slate",
  success: "border-emerald/15 bg-emerald/10 text-emerald",
  warning: "border-amber/20 bg-amber/10 text-amber-700",
  danger: "border-red-200 bg-red-50 text-red-700",
  checking: "border-slate/15 bg-slate/10 text-slate",
  online: "border-emerald/15 bg-emerald/10 text-emerald",
  offline: "border-red-200 bg-red-50 text-red-700",
  ULO: "border-cyan-200 bg-cyan-50 text-cyan-700",
  TOU: "border-orange-200 bg-orange-50 text-orange-700",
  Tiered: "border-green-200 bg-green-50 text-green-700",
  Unknown: "border-slate-200 bg-slate-100 text-slate-700",
};

export function StatusChip({ label, value, tone = "default" }: StatusChipProps) {
  return (
    <div className={cn("rounded-full border px-3.5 py-2 text-xs font-semibold shadow-soft", toneStyles[tone])}>
      <span className="mr-2 opacity-70">{label}</span>
      <span>{value}</span>
    </div>
  );
}
