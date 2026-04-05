import { LoaderCircle, SendHorizontal } from "lucide-react";
import { type FormEvent, type RefObject } from "react";

import type { AskResponse } from "../types/api";
import { AnswerCard } from "./AnswerCard";
import { ExampleQuestions } from "./ExampleQuestions";
import { SectionCard } from "./SectionCard";

type AskPanelProps = {
  question: string;
  onQuestionChange: (value: string) => void;
  onAsk: () => Promise<void>;
  loading: boolean;
  answer?: AskResponse | null;
  hasDocument: boolean;
  answerRef: RefObject<HTMLDivElement>;
};

export function AskPanel({
  question,
  onQuestionChange,
  onAsk,
  loading,
  answer,
  hasDocument,
  answerRef,
}: AskPanelProps) {
  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    await onAsk();
  }

  return (
    <SectionCard
      eyebrow="Questions"
      title="Question & Answer Workspace"
      description="Ask a plain-language question about the uploaded bill. The answer uses retrieved bill snippets first, then Ontario billing knowledge."
    >
      <div className="grid gap-6 lg:grid-cols-[1.05fr_0.95fr]">
        <div className="space-y-5">
          <ExampleQuestions onSelect={onQuestionChange} currentQuestion={question} />
          <form onSubmit={handleSubmit} className="rounded-3xl bg-white p-5 subtle-ring">
            <label htmlFor="question" className="mb-3 block text-sm font-semibold uppercase tracking-[0.2em] text-slate">
              Ask about this bill
            </label>
            <textarea
              id="question"
              value={question}
              onChange={(event) => onQuestionChange(event.target.value)}
              placeholder="Example: Why is my bill so high this month?"
              rows={6}
              className="w-full rounded-3xl border border-emerald/10 bg-canvas px-4 py-4 text-base text-ink outline-none transition placeholder:text-slate/70 focus:border-emerald/40 focus:bg-white"
            />
            <div className="mt-4 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
              <p className="text-sm text-slate">
                The ask button stays disabled until at least one uploaded document is available.
              </p>
              <button
                type="submit"
                disabled={!hasDocument || !question.trim() || loading}
                className="inline-flex items-center justify-center gap-2 rounded-full bg-ink px-5 py-3 text-sm font-semibold text-white transition hover:bg-ink/90 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {loading ? <LoaderCircle className="h-4 w-4 animate-spin" /> : <SendHorizontal className="h-4 w-4" />}
                {loading ? "Generating..." : "Ask the Assistant"}
              </button>
            </div>
          </form>
        </div>
        <div ref={answerRef}>
          <AnswerCard answer={answer} loading={loading} hasDocument={hasDocument} />
        </div>
      </div>
    </SectionCard>
  );
}
