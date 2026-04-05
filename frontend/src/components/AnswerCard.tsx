import { BookMarked, Radar, Sparkles } from "lucide-react";

import { formatPercent, normalizePlan } from "../lib/utils";
import type { AskResponse } from "../types/api";
import { EmptyState } from "./EmptyState";
import { StatusChip } from "./StatusChip";

type AnswerCardProps = {
  answer?: AskResponse | null;
  loading: boolean;
  hasDocument: boolean;
};

export function AnswerCard({ answer, loading, hasDocument }: AnswerCardProps) {
  if (!hasDocument) {
    return (
      <EmptyState
        icon={BookMarked}
        title="No document context yet"
        description="Upload an electricity bill to unlock grounded answers and supporting evidence."
      />
    );
  }

  if (!answer && !loading) {
    return (
      <EmptyState
        icon={Sparkles}
        title="No answer yet"
        description="Ask a question about the uploaded bill and the assistant will return a plain-language answer with evidence."
      />
    );
  }

  if (loading) {
    return (
      <div className="rounded-3xl bg-white p-6 subtle-ring">
        <div className="mb-5 flex items-center gap-3">
          <div className="h-10 w-10 animate-pulse rounded-2xl bg-emerald/10" />
          <div className="space-y-2">
            <div className="h-4 w-28 animate-pulse rounded-full bg-slate/10" />
            <div className="h-3 w-44 animate-pulse rounded-full bg-slate/10" />
          </div>
        </div>
        <div className="space-y-3">
          <div className="h-4 animate-pulse rounded-full bg-slate/10" />
          <div className="h-4 w-11/12 animate-pulse rounded-full bg-slate/10" />
          <div className="h-4 w-9/12 animate-pulse rounded-full bg-slate/10" />
        </div>
      </div>
    );
  }

  const plan = normalizePlan(answer?.detected_plan);
  const sources = answer?.sources || [];

  return (
    <div className="space-y-5">
      <div className="rounded-[32px] bg-white p-6 shadow-panel">
        <div className="mb-5 flex flex-wrap items-center gap-3">
          <StatusChip label="Plan" value={plan} tone={plan} />
          <StatusChip
            label="Confidence"
            value={formatPercent(answer?.detection_confidence)}
            tone={plan === "Unknown" ? "warning" : "default"}
          />
          <div className="inline-flex items-center gap-2 rounded-full bg-mist px-3 py-2 text-xs font-semibold text-emerald">
            <Radar className="h-4 w-4" />
            Grounded answer
          </div>
        </div>
        <p className="text-lg leading-8 text-ink md:text-xl">{answer?.answer || ""}</p>
      </div>

      <div className="rounded-3xl bg-white p-6 subtle-ring">
        <div className="mb-4 flex items-center gap-2">
          <BookMarked className="h-5 w-5 text-teal" />
          <h3 className="text-lg font-semibold text-ink">Supporting Evidence</h3>
        </div>
        {sources.length ? (
          <div className="grid gap-3">
            {sources.map((source, index) => (
              <div key={`${source.chunk_id || index}-${source.page_number || "x"}`} className="rounded-2xl bg-mist/70 p-4">
                <div className="mb-2 flex flex-wrap gap-2 text-xs font-semibold text-slate">
                  <span className="rounded-full bg-white px-3 py-1">Doc #{source.document_id ?? "N/A"}</span>
                  <span className="rounded-full bg-white px-3 py-1">
                    {source.document_name || "Uploaded bill context"}
                  </span>
                  <span className="rounded-full bg-white px-3 py-1">Page {source.page_number ?? "Unknown"}</span>
                </div>
                <p className="text-sm leading-6 text-ink">{source.snippet}</p>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-slate">No source snippets were returned for this answer.</p>
        )}
      </div>
    </div>
  );
}
