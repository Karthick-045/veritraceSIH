export interface ApiResponse<T> {
  data: T | null;
  error: { code: string; message: string } | null;
}

export interface Case {
  id: number;
  case_number: string;
  title: string;
  institution_name: string;
  status: string;
  review_date?: string;
  assigned_to_id?: number;
  created_at: string;
  updated_at: string;
  document_count: number;
  finding_count: number;
}

export interface DocumentItem {
  id: number;
  case_id: number;
  doc_type: string;
  original_filename: string;
  mime_type: string;
  file_size_bytes: number;
  sha256_hash: string;
  status: string;
  created_at: string;
}

export interface DocumentPage {
  page_number: number;
  extracted_text: string;
  ocr_engine: string;
  mean_confidence: number;
  layout_data?: Array<{ text: string; bbox: { x0: number; y0: number; x1: number; y1: number }; confidence: number }>;
  has_image: boolean;
}

export interface ExtractedField {
  id: number;
  case_id: number;
  document_id: number;
  page_number: number;
  field_key: string;
  raw_value: string;
  normalized_value?: string;
  confidence: number;
  bbox?: { x0: number; y0: number; x1: number; y1: number };
  is_ambiguous: boolean;
  review_status: string;
  extraction_method: string;
  verbatim_snippet?: string;
  document_name?: string;
}

export interface EvidenceItem {
  id: number;
  source_label: string;
  document_id: number;
  page_number: number;
  field_key: string;
  raw_value: string;
  normalized_value?: string;
  bbox?: { x0: number; y0: number; x1: number; y1: number };
  document_name?: string;
}

export interface Finding {
  id: number;
  case_id: number;
  analysis_run_id?: number;
  rule_code: string;
  rule_version: string;
  severity: string;
  title: string;
  explanation: string;
  uncertainty_note?: string;
  system_status: string;
  reviewer_status: string;
  superseded: boolean;
  created_at: string;
  evidence_items: EvidenceItem[];
}

export interface AuditEvent {
  id: number;
  case_id: number;
  user_id?: number;
  event_type: string;
  payload: any;
  created_at: string;
}

export interface BenchmarkRun {
  id: number;
  total_cases: number;
  precision: number;
  recall: number;
  f1_score: number;
  tp_count: number;
  fp_count: number;
  fn_count: number;
  duration_ms: number;
  created_at: string;
  case_results: Array<{
    case_key: string;
    expected_rules: string[];
    detected_rules: string[];
    tp: number;
    fp: number;
    fn: number;
    duration_ms: number;
  }>;
}

export interface DashboardSummary {
  total_cases: number;
  total_documents: number;
  findings_by_severity: Record<string, number>;
  system_truth_states: Record<string, number>;
  recent_activity: AuditEvent[];
  latest_benchmark?: BenchmarkRun;
}

export interface ValidationRule {
  id: number;
  rule_code: string;
  name: string;
  description: string;
  version: string;
  is_active: boolean;
  severity: string;
}

const API_BASE = '/api';

async function request<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const token = localStorage.getItem('token');
  const headers: Record<string, string> = {
    ...(options?.headers as Record<string, string> || {}),
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  const res = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (!res.ok) {
    let errMessage = `HTTP error ${res.status}`;
    try {
      const errJson = await res.json();
      if (errJson?.error?.message) {
        errMessage = errJson.error.message;
      }
    } catch {}
    throw new Error(errMessage);
  }

  const json: ApiResponse<T> = await res.json();
  if (json.error) {
    throw new Error(json.error.message);
  }
  return json.data as T;
}

export const api = {
  // Cases
  getCases: () => request<Case[]>('/cases'),
  getCase: (id: number) => request<Case>(`/cases/${id}`),
  createCase: (payload: { case_number: string; title: string; institution_name: string; review_date?: string }) =>
    request<Case>('/cases', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    }),

  // Documents
  getDocuments: (caseId: number) => request<DocumentItem[]>(`/cases/${caseId}/documents`),
  getDocumentPage: (docId: number, pageNum: number) => request<DocumentPage>(`/documents/${docId}/pages/${pageNum}`),
  uploadDocument: (caseId: number, file: File, docType: string = 'general') => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('doc_type', docType);
    return request<DocumentItem>(`/cases/${caseId}/documents`, {
      method: 'POST',
      body: formData,
    });
  },

  // Analysis & Findings
  analyzeCase: (caseId: number) => request<any>(`/cases/${caseId}/analyze`, { method: 'POST' }),
  reproduceRun: (runId: number) => request<any>(`/runs/${runId}/reproduce`, { method: 'POST' }),
  getFindings: (caseId: number) => request<Finding[]>(`/cases/${caseId}/findings`),
  reviewFinding: (findingId: number, decision: string, comment: string) =>
    request<Finding>(`/findings/${findingId}/review`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ decision, comment }),
    }),

  // Fields
  getFields: (caseId: number) => request<ExtractedField[]>(`/cases/${caseId}/fields`),
  correctField: (fieldId: number, correctedValue: string, reason?: string) =>
    request<ExtractedField>(`/fields/${fieldId}/correct`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ corrected_value: correctedValue, reason }),
    }),

  // Graph
  getCaseGraph: (caseId: number) => request<{ nodes: any[]; edges: any[] }>(`/cases/${caseId}/graph`),

  // Audit
  getCaseAudit: (caseId: number) => request<AuditEvent[]>(`/cases/${caseId}/audit`),

  // Benchmark
  runBenchmark: () => request<BenchmarkRun>('/benchmarks/run', { method: 'POST' }),
  getBenchmarks: () => request<BenchmarkRun[]>('/benchmarks'),

  // Rules
  getRules: () => request<ValidationRule[]>('/rules'),
  updateRule: (id: number, payload: Partial<ValidationRule>) =>
    request<ValidationRule>(`/rules/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    }),

  // Dashboard
  getDashboardSummary: () => request<DashboardSummary>('/dashboard/summary'),
};
