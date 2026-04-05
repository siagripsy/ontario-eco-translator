import { AlertCircle, BadgeInfo, Sparkles } from "lucide-react";

import { formatPercent, normalizePlan } from "../lib/utils";
import type { AskResponse } from "../types/api";
import { EmptyState } from "./EmptyState";
import { SectionCard } from "./SectionCard";
import { StatusChip } from "./StatusChip";

type AnalysisSummaryCardProps = {
  answer?: AskResponse | null;
  hasDocument: boolean;
};

const summaries: Record<string, string> = {
  ULO: "This bill appears to use the ULO pricing model because overnight pricing clues were found in the bill text.",
  TOU: "This bill appears to use Time-of-Use pricing because peak-period labels were detected in the uploaded bill.",
  Tiered: "This bill appears to use Tiered pricing because usage tiers were identified instead of time-based periods.",
  Unknown:
    "The system could not confidently identify the pricing plan yet. It will fall back to broader Ontario billing guidance when answering.",
};

export function AnalysisSummaryCard({ answer, hasDocument }: AnalysisSummaryCardProps) {
  if (!hasDocument) {
    return (
      <SectionCard
        eyebrow="Bill Analysis"
        title="Plan Detection Summary"
        description="Once a bill is available and you ask a question, the assistant will surface plan evidence and a confidence score."
      >
        <EmptyState
          icon={BadgeInfo}
          title="No analysis yet"
          description="Upload a bill first. Then ask a question like “What billing plan is used in this bill?” to generate the plan summary."
        />
      </SectionCard>
    );
  }

  if (!answer) {
    return (
      <SectionCard
        eyebrow="Bill Analysis"
        title="Plan Detection Summary"
        description="The backend returns plan metadata as part of the grounded answer workflow."
      >
        <EmptyState
          icon={Sparkles}
          title="Ready to detect the plan"
          description="The bill is uploaded. Ask a question and the workspace will show the detected plan, confidence, and bill clues here."
        />
      </SectionCard>
    );
  }

  const plan = normalizePlan(answer.detected_plan);
  const evidence = answer.detection_evidence || [];

  return (
    <SectionCard
      eyebrow="Bill Analysis"
      title="Plan Detection Summary"
      description="This summary is inferred from the uploaded bill text and returned directly by the backend answer workflow."
    >
      <div className="grid gap-4 md:grid-cols-[1.1fr_0.9fr]">
        <div className="rounded-3xl bg-gradient-to-br from-mist to-white p-5 subtle-ring">
          <div className="flex flex-wrap items-center gap-3">
            <StatusChip label="Detected Plan" value={plan} tone={plan} />
            <StatusChip label="Confidence" value={formatPercent(answer.detection_confidence)} tone="default" />
          </div>
          <p className="mt-4 text-base leading-7 text-ink">{summaries[plan]}</p>
          {plan === "Unknown" ? (
            <div className="mt-4 flex items-start gap-3 rounded-2xl border border-amber/20 bg-amber/10 p-4 text-sm text-amber-900">
              <AlertCircle className="mt-0.5 h-5 w-5 shrink-0" />
              <p>The assistant will answer carefully using fallback plan guidance instead of inventing a billing plan.</p>
            </div>
          ) : null}
        </div>
        <div className="rounded-3xl bg-white p-5 subtle-ring">
          <p className="text-sm font-semibold uppercase tracking-[0.2em] text-slate">Bill Clues</p>
          {evidence.length ? (
            <ul className="mt-4 space-y-3">
              {evidence.map((item) => (
                <li key={item} className="flex items-start gap-3 rounded-2xl bg-mist/70 px-4 py-3 text-sm text-ink">
                  <span className="mt-1 h-2 w-2 rounded-full bg-emerald" />
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="mt-4 text-sm leading-6 text-slate">No strong clues were returned by the backend for this answer.</p>
          )}
        </div>
      </div>
    </SectionCard>
  );
}
