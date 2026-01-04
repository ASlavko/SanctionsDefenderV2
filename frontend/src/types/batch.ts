// Decision management types
export type MatchStatus =
  | "CONFIRMED"
  | "CLEARED"
  | "PENDING"
  | "REVISIT"
  | "NO_MATCH";

export interface MatchDecision {
  id: number;
  search_term_normalized: string;
  sanction_id: string;
  decision: MatchStatus;
  comment?: string;
  created_at: string;
  user_id: string;
  revoked: boolean;
}

export interface DecisionAudit {
  id: number;
  action: string;
  old_value: string | null;
  new_value: string | null;
  user_id: string;
  timestamp: string;
  comment?: string;
}
export interface BatchResponse {
  id: number;
  filename: string;
  uploaded_at: string;
  total_records: number;
  flagged_count: number | null;
  status: string;
}

export interface ScreeningMatch {
  sanction_id: string;
  match_score: number;
  match_name: string;
}

export interface ScreeningResultResponse {
  id: number;
  input_name: string;
  match_status: string;
  matches: ScreeningMatch[];
}

export interface BatchDetailResponse {
  batch: BatchResponse;
  results: ScreeningResultResponse[];
}
