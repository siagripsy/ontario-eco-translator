import { LoaderCircle, UploadCloud } from "lucide-react";
import { useMemo, useRef, useState } from "react";

import { cn } from "../lib/utils";
import type { DocumentUploadResponse } from "../types/api";
import { SectionCard } from "./SectionCard";

type UploadCardProps = {
  onUpload: (file: File) => Promise<void>;
  uploadResult?: DocumentUploadResponse | null;
  busy: boolean;
};

export function UploadCard({ onUpload, uploadResult, busy }: UploadCardProps) {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const fileLabel = useMemo(() => selectedFile?.name || uploadResult?.document_name || "No file selected", [
    selectedFile,
    uploadResult,
  ]);

  async function submitFile(file: File | null) {
    if (!file || busy) return;
    setSelectedFile(file);
    await onUpload(file);
  }

  return (
    <SectionCard
      eyebrow="Upload"
      title="Bill Upload"
      description="Drop in a PDF electricity bill and the system will index it for grounded question answering."
      action={
        <button
          type="button"
          onClick={() => submitFile(selectedFile)}
          disabled={!selectedFile || busy}
          className="inline-flex items-center gap-2 rounded-full bg-emerald px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-emerald/90 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {busy ? <LoaderCircle className="h-4 w-4 animate-spin" /> : <UploadCloud className="h-4 w-4" />}
          {busy ? "Uploading..." : "Upload PDF"}
        </button>
      }
    >
      <div
        onDragOver={(event) => {
          event.preventDefault();
          setDragActive(true);
        }}
        onDragLeave={() => setDragActive(false)}
        onDrop={(event) => {
          event.preventDefault();
          setDragActive(false);
          const file = event.dataTransfer.files?.[0] || null;
          if (file) void submitFile(file);
        }}
        onClick={() => inputRef.current?.click()}
        className={cn(
          "group cursor-pointer rounded-[28px] border border-dashed px-6 py-10 transition",
          dragActive
            ? "border-emerald bg-emerald/5 shadow-soft"
            : "border-emerald/20 bg-gradient-to-br from-white to-mist hover:border-emerald/40 hover:bg-emerald/5",
        )}
      >
        <input
          ref={inputRef}
          type="file"
          accept="application/pdf"
          className="hidden"
          onChange={(event) => {
            const file = event.target.files?.[0] || null;
            if (file) setSelectedFile(file);
          }}
        />
        <div className="mx-auto flex max-w-lg flex-col items-center text-center">
          <div className="mb-5 flex h-16 w-16 items-center justify-center rounded-2xl bg-white shadow-soft transition group-hover:scale-105">
            <UploadCloud className="h-7 w-7 text-emerald" />
          </div>
          <h3 className="text-xl font-semibold text-ink">Drag and drop your bill PDF</h3>
          <p className="mt-2 text-sm leading-6 text-slate">
            Click to browse or drop a document here. Supported: PDF electricity bills.
          </p>
          <div className="mt-5 rounded-full bg-white px-4 py-2 text-sm font-semibold text-ink shadow-soft">
            {fileLabel}
          </div>
          {uploadResult ? (
            <div className="mt-4 flex flex-wrap items-center justify-center gap-2 text-xs font-semibold text-emerald">
              <span className="rounded-full bg-emerald/10 px-3 py-1">Document ID #{uploadResult.document_id}</span>
              <span className="rounded-full bg-emerald/10 px-3 py-1">{uploadResult.chunk_count} chunks indexed</span>
            </div>
          ) : null}
        </div>
      </div>
    </SectionCard>
  );
}
