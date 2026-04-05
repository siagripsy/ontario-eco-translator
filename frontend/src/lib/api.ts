import type {
  AskRequest,
  AskResponse,
  DocumentListItem,
  DocumentUploadResponse,
  HealthResponse,
} from "../types/api";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "") || "";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, init);
  const contentType = response.headers.get("content-type") || "";
  const payload = contentType.includes("application/json") ? await response.json() : await response.text();

  if (!response.ok) {
    const detail =
      typeof payload === "object" && payload && "detail" in payload
        ? String((payload as { detail?: unknown }).detail)
        : "The server returned an unexpected error.";
    throw new Error(detail);
  }

  return payload as T;
}

export const api = {
  baseUrl: API_BASE_URL,
  health: () => request<HealthResponse>("/health"),
  dbHealth: () => request<HealthResponse>("/db/health"),
  listDocuments: () => request<DocumentListItem[]>("/documents"),
  uploadDocument: (file: File) => {
    const formData = new FormData();
    formData.append("file", file);

    return request<DocumentUploadResponse>("/documents/upload", {
      method: "POST",
      body: formData,
    });
  },
  askQuestion: (body: AskRequest) =>
    request<AskResponse>("/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }),
};
