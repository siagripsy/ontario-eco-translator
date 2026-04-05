import { Activity, ArrowUpRight, BotMessageSquare, ShieldCheck } from "lucide-react";
import { startTransition, useEffect, useMemo, useRef, useState } from "react";

import { AnalysisSummaryCard } from "./components/AnalysisSummaryCard";
import { AskPanel } from "./components/AskPanel";
import { DocumentList } from "./components/DocumentList";
import { EmptyState } from "./components/EmptyState";
import { ErrorBanner } from "./components/ErrorBanner";
import { HeaderStatus } from "./components/HeaderStatus";
import { UploadCard } from "./components/UploadCard";
import { api } from "./lib/api";
import { normalizePlan } from "./lib/utils";
import type { AskResponse, BackendStatus, DocumentListItem, DocumentUploadResponse } from "./types/api";

export default function App() {
  const [backendStatus, setBackendStatus] = useState<BackendStatus>("checking");
  const [dbHealthy, setDbHealthy] = useState<boolean | null>(null);
  const [documents, setDocuments] = useState<DocumentListItem[]>([]);
  const [documentsLoading, setDocumentsLoading] = useState(true);
  const [uploadBusy, setUploadBusy] = useState(false);
  const [askBusy, setAskBusy] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [question, setQuestion] = useState("What billing plan is used in this bill?");
  const [uploadResult, setUploadResult] = useState<DocumentUploadResponse | null>(null);
  const [latestAnswer, setLatestAnswer] = useState<AskResponse | null>(null);
  const answerRef = useRef<HTMLDivElement>(null);

  async function refreshHealth() {
    try {
      const health = await api.health();
      startTransition(() => {
        setBackendStatus(health.status === "ok" ? "online" : "offline");
      });
    } catch {
      startTransition(() => {
        setBackendStatus("offline");
        setDbHealthy(false);
      });
      return;
    }

    try {
      const dbHealth = await api.dbHealth();
      startTransition(() => {
        setDbHealthy(dbHealth.status === "ok");
      });
    } catch {
      startTransition(() => {
        setDbHealthy(false);
      });
    }
  }

  async function refreshDocuments() {
    setDocumentsLoading(true);
    try {
      const nextDocuments = await api.listDocuments();
      startTransition(() => setDocuments(nextDocuments));
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Could not load uploaded documents.");
    } finally {
      setDocumentsLoading(false);
    }
  }

  useEffect(() => {
    void refreshHealth();
    void refreshDocuments();
  }, []);

  useEffect(() => {
    if (!latestAnswer) return;
    answerRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
  }, [latestAnswer]);

  const latestDocumentId = uploadResult?.document_id ?? documents[0]?.id ?? null;
  const hasDocuments = documents.length > 0 || !!uploadResult;
  const detectedPlan = normalizePlan(latestAnswer?.detected_plan);

  const heroMetrics = useMemo(
    () => [
      {
        label: "Backend API",
        value: backendStatus === "online" ? "Connected" : backendStatus === "offline" ? "Unavailable" : "Checking",
        icon: ShieldCheck,
      },
      {
        label: "Indexed bills",
        value: String(documents.length),
        icon: Activity,
      },
      {
        label: "Grounded answers",
        value: latestAnswer ? "Ready" : "Waiting",
        icon: BotMessageSquare,
      },
    ],
    [backendStatus, documents.length, latestAnswer],
  );

  async function handleUpload(file: File) {
    setErrorMessage(null);
    setUploadBusy(true);
    try {
      const result = await api.uploadDocument(file);
      setUploadResult(result);
      await refreshDocuments();
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Upload failed.");
    } finally {
      setUploadBusy(false);
    }
  }

  async function handleAsk() {
    if (!question.trim() || !hasDocuments) return;

    setErrorMessage(null);
    setAskBusy(true);
    try {
      const response = await api.askQuestion({ question: question.trim() });
      setLatestAnswer(response);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Could not generate an answer.");
    } finally {
      setAskBusy(false);
    }
  }

  return (
    <div className="min-h-screen bg-hero-radial px-4 py-8 text-ink sm:px-6 lg:px-8">
      <div className="mx-auto max-w-7xl space-y-8">
        <header className="glass-panel overflow-hidden p-8 md:p-10">
          <div className="grid gap-8 lg:grid-cols-[1.2fr_0.8fr]">
            <div className="space-y-6">
              <div className="inline-flex items-center gap-2 rounded-full border border-emerald/10 bg-white/90 px-3 py-2 text-xs font-semibold uppercase tracking-[0.24em] text-emerald shadow-soft">
                <span className="h-2.5 w-2.5 rounded-full bg-emerald" />
                Ontario Eco-Translator
              </div>
              <div className="space-y-4">
                <h1 className="display-title">Upload your electricity bill and ask questions in plain language.</h1>
                <p className="max-w-2xl text-base leading-8 text-slate md:text-lg">
                  A polished demo workspace for Ontario electricity bill analysis. Upload a PDF, detect the billing
                  plan, and get grounded explanations backed by the uploaded bill.
                </p>
              </div>
              <HeaderStatus backendStatus={backendStatus} hasDocument={hasDocuments} detectedPlan={detectedPlan} />
            </div>
            <div className="grid gap-4 sm:grid-cols-3 lg:grid-cols-1">
              {heroMetrics.map(({ label, value, icon: Icon }) => (
                <div key={label} className="rounded-[28px] bg-white/90 p-5 shadow-soft subtle-ring">
                  <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-mist text-emerald">
                    <Icon className="h-6 w-6" />
                  </div>
                  <p className="text-sm font-semibold uppercase tracking-[0.18em] text-slate">{label}</p>
                  <p className="mt-2 text-2xl font-semibold text-ink">{value}</p>
                </div>
              ))}
            </div>
          </div>
        </header>

        {errorMessage ? <ErrorBanner message={errorMessage} /> : null}

        {backendStatus === "offline" ? (
          <div className="glass-panel p-8">
            <EmptyState
              icon={ArrowUpRight}
              title="Backend unavailable"
              description={`The frontend could not reach the FastAPI backend at ${api.baseUrl}. Start the API and refresh the page.`}
            />
          </div>
        ) : null}

        <div className="grid gap-8 xl:grid-cols-[1.15fr_0.85fr]">
          <div className="space-y-8">
            <UploadCard onUpload={handleUpload} uploadResult={uploadResult} busy={uploadBusy} />
            <AskPanel
              question={question}
              onQuestionChange={setQuestion}
              onAsk={handleAsk}
              loading={askBusy}
              answer={latestAnswer}
              hasDocument={hasDocuments}
              answerRef={answerRef}
            />
          </div>
          <div className="space-y-8">
            <AnalysisSummaryCard answer={latestAnswer} hasDocument={hasDocuments} />
            <DocumentList documents={documents} loading={documentsLoading} latestDocumentId={latestDocumentId} />
            <div className="glass-panel p-6">
              <p className="section-title">System Notes</p>
              <div className="mt-4 space-y-3 text-sm leading-6 text-slate">
                <p>
                  Backend status: <span className="font-semibold text-ink">{backendStatus}</span>
                </p>
                <p>
                  Database health:{" "}
                  <span className="font-semibold text-ink">
                    {dbHealthy === null ? "Checking" : dbHealthy ? "Healthy" : "Unavailable"}
                  </span>
                </p>
                <p>
                  The UI is resilient to missing optional fields and uses the backend response exactly as returned by
                  FastAPI.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
