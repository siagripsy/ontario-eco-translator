import { Files, LoaderCircle } from "lucide-react";

import { formatDateTime } from "../lib/utils";
import type { DocumentListItem } from "../types/api";
import { EmptyState } from "./EmptyState";
import { SectionCard } from "./SectionCard";
import { StatusChip } from "./StatusChip";

type DocumentListProps = {
  documents: DocumentListItem[];
  loading: boolean;
  latestDocumentId?: number | null;
};

export function DocumentList({ documents, loading, latestDocumentId }: DocumentListProps) {
  return (
    <SectionCard
      eyebrow="Library"
      title="Uploaded Documents"
      description="A compact view of the ingested bills currently available to the assistant."
    >
      {loading ? (
        <div className="flex items-center gap-3 rounded-3xl bg-mist/60 p-5 text-sm text-slate">
          <LoaderCircle className="h-5 w-5 animate-spin text-emerald" />
          Loading uploaded documents...
        </div>
      ) : documents.length ? (
        <div className="space-y-3">
          {documents.map((document, index) => {
            const isLatest = document.id === latestDocumentId || (!latestDocumentId && index === 0);
            return (
              <article
                key={document.id}
                className={`rounded-3xl p-4 transition ${
                  isLatest ? "bg-emerald/[0.08] subtle-ring shadow-soft" : "bg-white subtle-ring"
                }`}
              >
                <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
                  <div className="space-y-2">
                    <div className="flex flex-wrap items-center gap-2">
                      <h3 className="text-base font-semibold text-ink">{document.document_name}</h3>
                      {isLatest ? (
                        <span className="rounded-full bg-emerald px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.16em] text-white">
                          Latest
                        </span>
                      ) : null}
                    </div>
                    <div className="flex flex-wrap gap-2 text-xs font-semibold text-slate">
                      <span className="rounded-full bg-mist px-3 py-1">Document #{document.id}</span>
                      <span className="rounded-full bg-mist px-3 py-1">{document.chunk_count} chunks</span>
                      <span className="rounded-full bg-mist px-3 py-1">{formatDateTime(document.uploaded_at)}</span>
                    </div>
                  </div>
                  <StatusChip
                    label="Status"
                    value={document.status}
                    tone={document.status === "processed" ? "success" : document.status === "failed" ? "danger" : "warning"}
                  />
                </div>
              </article>
            );
          })}
        </div>
      ) : (
        <EmptyState
          icon={Files}
          title="No uploaded documents"
          description="Upload a PDF bill to populate the document library and enable grounded answers."
        />
      )}
    </SectionCard>
  );
}
