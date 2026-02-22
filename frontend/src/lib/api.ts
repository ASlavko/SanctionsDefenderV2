// Single screening API
export interface SingleScreeningResult {
  matches: any[];
  result_count: number;
}

export async function runSingleScreening({
  search_term,
  search_type,
  user_id,
  company_id,
  threshold = 85,
}: {
  search_term: string;
  search_type: string;
  user_id: string;
  company_id: string;
  threshold?: number;
}): Promise<SingleScreeningResult> {
  const res = await fetch(apiUrl("/api/v1/single_screening/"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ search_term, search_type, user_id, company_id, threshold }),
  });
  if (!res.ok) throw new Error("Failed to run single screening");
  return res.json();
}

// Search log history API
export interface SearchLogEntry {
  id: number;
  timestamp: string;
  search_term: string;
  search_type: string;
  result_count: number;
  user_id: string;
  company_id: string;
}

export async function fetchSearchLogHistory({
  company_id,
  user_id,
  skip = 0,
  limit = 50,
}: {
  company_id: string;
  user_id?: string;
  skip?: number;
  limit?: number;
}): Promise<SearchLogEntry[]> {
  const params = new URLSearchParams({ company_id, skip: String(skip), limit: String(limit) });
  if (user_id) params.append("user_id", user_id);
  const res = await fetch(apiUrl(`/api/v1/search_log/?${params.toString()}`));
  if (!res.ok) throw new Error("Failed to fetch search log history");
  return res.json();
}
// Paginated batch detail response
export interface PaginatedBatchDetailResponse {
  batch: BatchResponse;
  results: ScreeningResultResponse[];
  total: number;
}

// Fetch paginated and filtered batch results
export async function fetchBatchDetailPaginated(
  batchId: string,
  params: { limit?: number; offset?: number; status?: string; search?: string }
): Promise<PaginatedBatchDetailResponse> {
  const query = new URLSearchParams();
  if (params.limit) query.append("limit", params.limit.toString());
  if (params.offset) query.append("offset", params.offset.toString());
  if (params.status) query.append("status", params.status);
  if (params.search) query.append("search", params.search);
  const res = await fetch(apiUrl(`/api/v1/batch/${batchId}?${query.toString()}`));
  if (!res.ok) throw new Error("Failed to load batch detail");
  return res.json();
}
import type { MatchDecision, DecisionAudit, MatchStatus } from "@/types/batch";

// Create a new decision
export async function createDecision(
  search_term_normalized: string,
  sanction_id: string,
  decision: MatchStatus,
  user_id: string,
  comment?: string
): Promise<MatchDecision> {
  const res = await fetch(apiUrl("/api/v1/decision/create"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      search_term_normalized,
      sanction_id,
      decision,
      user_id,
      comment,
    }),
  });
  if (!res.ok) throw new Error("Failed to create decision");
  return res.json();
}

// List all decisions (optionally only active)
export async function listDecisions(
  active_only = true
): Promise<MatchDecision[]> {
  const res = await fetch(
    apiUrl(`/api/v1/decision/list?active_only=${active_only}`)
  );
  if (!res.ok) throw new Error("Failed to list decisions");
  return res.json();
}

// Get audit history for a decision
export async function getDecisionAudit(
  decision_id: number
): Promise<DecisionAudit[]> {
  const res = await fetch(apiUrl(`/api/v1/decision/audit/${decision_id}`));
  if (!res.ok) throw new Error("Failed to fetch audit history");
  return res.json();
}
const apiBase = process.env.NEXT_PUBLIC_API_BASE ?? "http://127.0.0.1:8001";

export function apiUrl(path: string) {
  const trimmed = path.startsWith("/") ? path.slice(1) : path;
  return `${apiBase}/${trimmed}`;
}

// Sanction List KPI API
export interface SanctionListBreakdown {
  individual_count: number;
  entity_count: number;
  aircraft_count: number;
  vessel_count: number;
  other_count: number;
}

export interface SanctionListKPI {
  source: string;
  last_update: string | null;
  records_added: number;
  records_updated: number;
  records_removed: number;
  total_records: number;
  breakdown: SanctionListBreakdown;
}

export async function fetchSanctionListKPIs(days: number = 1): Promise<SanctionListKPI[]> {
  const url = days > 1 ? `/api/v1/kpi/sanction-lists?days=${days}` : "/api/v1/kpi/sanction-lists";
  const res = await fetch(apiUrl(url));
  if (!res.ok) throw new Error("Failed to fetch sanction list KPIs");
  return res.json();
}

