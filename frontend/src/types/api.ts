export type HealthResponse = {
  status?: string;
};

export type DocumentListItem = {
  id: number;
  document_name: string;
  source_type: string;
  source_path?: string | null;
  uploaded_at: string;
  status: string;
  chunk_count: number;
};

export type DocumentUploadResponse = {
  document_id: number;
  document_name: string;
  status: string;
  chunk_count: number;
  processing_run_id: number;
};

export type AskRequest = {
  question: string;
  top_k?: number;
};

export type AnswerSource = {
  document_id?: number | null;
  document_name?: string | null;
  chunk_id?: number | null;
  page_number?: number | null;
  section_title?: string | null;
  snippet: string;
  score?: number | null;
};

export type AskResponse = {
  answer: string;
  detected_plan?: string;
  detection_confidence?: number;
  detection_evidence?: string[];
  sources?: AnswerSource[];
};

export type BackendStatus = "checking" | "online" | "offline";

export type PlanKind = "ULO" | "TOU" | "Tiered" | "Unknown";
