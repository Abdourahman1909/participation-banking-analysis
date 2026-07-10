/** Mirror of the HTTP contract (ADR 0022, banking_analysis/api/schemas.py). */

export interface Stats {
  banks: number | null;
  campaigns: number | null;
  last_collection: string | null;
  db_ok: boolean;
}

export interface CampaignItem {
  bank: string;
  title: string;
  campaign_type: string;
  profit_share_rate: string | null;
  maturity_months: string | null;
  cost_amount: string | null;
  evidence_quote: string;
  rate_normalized: number | null;
  term_months: number | null;
  is_valid: boolean;
}

export interface CampaignList {
  items: CampaignItem[];
  is_sample: boolean;
}

export interface Source {
  bank: string;
  title: string | null;
  field: string | null;
  value: string | null;
  evidence_quote: string | null;
}

export interface ChatResponse {
  answer: string;
  sources: Source[];
  is_preview: boolean;
}

export interface PipelineStatus {
  db_ok: boolean;
  banks: number | null;
  collected: number | null;
  runs_total: number | null;
  extracted: number | null;
  validated: number | null;
  scraped_banks: number | null;
  last_collection: string | null;
  model_ok: boolean;
  model_detail: string;
}

export type Step = "collection" | "extraction" | "validation";

export interface RunInfo {
  id: number;
  step: Step;
  started_at: string;
  finished_at: string | null;
  ok: boolean | null;
}

/** One SSE payload from /api/pipeline/runs/{id}/events. */
export interface RunEvent {
  seq: number;
  type: string;
  [key: string]: unknown;
}
