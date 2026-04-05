import { Database, FileCheck2, Radar } from "lucide-react";

import { normalizePlan } from "../lib/utils";
import type { BackendStatus } from "../types/api";
import { StatusChip } from "./StatusChip";

type HeaderStatusProps = {
  backendStatus: BackendStatus;
  hasDocument: boolean;
  detectedPlan?: string;
};

export function HeaderStatus({ backendStatus, hasDocument, detectedPlan }: HeaderStatusProps) {
  const plan = normalizePlan(detectedPlan);

  return (
    <div className="flex flex-wrap gap-3">
      <div className="flex items-center gap-2 rounded-full border border-white/80 bg-white/80 px-2 py-2 shadow-soft">
        <Database className="h-4 w-4 text-emerald" />
        <StatusChip
          label="Backend"
          value={backendStatus === "online" ? "Online" : backendStatus === "offline" ? "Offline" : "Checking"}
          tone={backendStatus}
        />
      </div>
      <div className="flex items-center gap-2 rounded-full border border-white/80 bg-white/80 px-2 py-2 shadow-soft">
        <FileCheck2 className="h-4 w-4 text-teal" />
        <StatusChip
          label="Document"
          value={hasDocument ? "Uploaded" : "No Document"}
          tone={hasDocument ? "success" : "default"}
        />
      </div>
      <div className="flex items-center gap-2 rounded-full border border-white/80 bg-white/80 px-2 py-2 shadow-soft">
        <Radar className="h-4 w-4 text-amber" />
        <StatusChip label="Plan" value={plan} tone={plan} />
      </div>
    </div>
  );
}
