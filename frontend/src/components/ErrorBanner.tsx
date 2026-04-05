import { AlertTriangle } from "lucide-react";

type ErrorBannerProps = {
  message: string;
};

export function ErrorBanner({ message }: ErrorBannerProps) {
  return (
    <div className="glass-panel border border-red-200/80 bg-red-50/90 p-4 text-sm text-red-800">
      <div className="flex items-start gap-3">
        <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0" />
        <p>{message}</p>
      </div>
    </div>
  );
}
