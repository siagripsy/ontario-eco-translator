import { Lightbulb } from "lucide-react";

import { cn } from "../lib/utils";

const EXAMPLE_QUESTIONS = [
  "What billing plan is used in this bill?",
  "Why is my electricity bill high?",
  "What is the delivery charge?",
  "Is this bill using ULO or TOU?",
  "How can I reduce my electricity cost?",
  "Why is the overnight rate cheaper?",
];

type ExampleQuestionsProps = {
  onSelect: (question: string) => void;
  currentQuestion: string;
};

export function ExampleQuestions({ onSelect, currentQuestion }: ExampleQuestionsProps) {
  return (
    <div className="rounded-3xl bg-mist/60 p-5 subtle-ring">
      <div className="mb-4 flex items-center gap-2">
        <Lightbulb className="h-5 w-5 text-amber" />
        <h3 className="text-sm font-semibold uppercase tracking-[0.2em] text-slate">Example Questions</h3>
      </div>
      <div className="flex flex-wrap gap-3">
        {EXAMPLE_QUESTIONS.map((question) => (
          <button
            key={question}
            type="button"
            onClick={() => onSelect(question)}
            className={cn(
              "rounded-full border px-4 py-2 text-sm font-semibold transition",
              currentQuestion === question
                ? "border-emerald bg-emerald text-white"
                : "border-emerald/15 bg-white text-ink hover:border-emerald/35 hover:bg-emerald/5",
            )}
          >
            {question}
          </button>
        ))}
      </div>
    </div>
  );
}
