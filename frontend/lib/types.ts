// Shared type contracts aligned with backend Pydantic schemas

export type TriageLabel = 'STP' | 'REVIEW' | 'HIGH_RISK';
export type DecisionStatus = 'APPROVE' | 'REVIEW' | 'REJECT' | 'PENDING';
export type ForensicsRisk = 'LOW' | 'MED' | 'HIGH';
export type RunStatus = 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED';

export interface User {
  id: string;
  email: string;
  name: string;
  role: 'admin' | 'adjuster' | 'reviewer';
  created_at: string;
}

export interface Claim {
  id: string;
  claim_number: string;
  customer_name: string;
  customer_email: string;
  policy_number: string;
  claim_type: string;
  amount: number;
  currency: string;
  incident_date: string;
  incident_location: string;
  description: string;
  triage_label: TriageLabel;
  fraud_score: number;
  risk_score: number;
  decision_status: DecisionStatus;
  confidence: number;
  fast_lane_eligible: boolean;
  created_at: string;
  updated_at: string;
  last_run_id?: string;
}

export interface ClaimDocument {
  id: string;
  claim_id: string;
  filename: string;
  file_type: string;
  file_size: number;
  storage_path: string;
  uploaded_at: string;
  forensics_risk: ForensicsRisk;
  forensics_signals: DocForensicsSignal[];
}

export interface DocForensicsSignal {
  id: string;
  document_id: string;
  signal_type: string;
  severity: ForensicsRisk;
  description: string;
  details: Record<string, unknown>;
  created_at: string;
}

export interface Extraction {
  id: string;
  claim_id: string;
  run_id: string;
  extracted_data: Record<string, unknown>;
  schema_valid: boolean;
  validation_errors?: string[];
  created_at: string;
}

export interface PolicyDocument {
  id: string;
  name: string;
  filename: string;
  file_type: string;
  storage_path: string;
  indexed: boolean;
  chunk_count: number;
  uploaded_at: string;
  indexed_at?: string;
}

export interface PolicyMatch {
  chunk_id: string;
  document_name: string;
  content: string;
  relevance_score: number;
  page_number?: number;
  section?: string;
}

export interface RiskScore {
  id: string;
  claim_id: string;
  run_id: string;
  overall_score: number;
  factors: RiskFactor[];
  created_at: string;
}

export interface RiskFactor {
  name: string;
  score: number;
  weight: number;
  description: string;
}

export interface Decision {
  id: string;
  claim_id: string;
  run_id: string;
  status: DecisionStatus;
  confidence: number;
  rationale: string;
  next_actions: string[];
  auto_approved: boolean;
  created_at: string;
}

export interface AuditEvent {
  id: string;
  claim_id?: string;
  run_id?: string;
  event_type: string;
  actor: string;
  payload: Record<string, unknown>;
  created_at: string;
}

export interface Run {
  id: string;
  claim_id: string;
  status: RunStatus;
  current_node?: string;
  started_at: string;
  completed_at?: string;
  duration_ms?: number;
  provider: string;
  trace_id?: string;
  error_message?: string;
}

export interface FraudScenario {
  id: string;
  name: string;
  category: string;
  description: string;
  threshold: number;
  enabled: boolean;
  hits_count: number;
  created_at: string;
}

export interface FraudHit {
  id: string;
  claim_id: string;
  run_id: string;
  scenario_id: string;
  scenario_name: string;
  score: number;
  explanation: string;
  created_at: string;
}

export interface FastLaneOverride {
  id: string;
  claim_id: string;
  reason: string;
  overridden_by: string;
  created_at: string;
}

export interface ConversationTranscript {
  id: string;
  claim_id?: string;
  messages: ConversationMessage[];
  created_at: string;
  completed_at?: string;
}

export interface ConversationMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  extracted_data?: Record<string, unknown>;
}

// API Response types
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface RunPipelineResponse {
  run_id: string;
  status: RunStatus;
  message: string;
}

export interface KnowledgeTestResponse {
  query: string;
  results: PolicyMatch[];
  latency_ms: number;
}

export interface HealthResponse {
  status: 'healthy' | 'unhealthy';
  version: string;
  database: boolean;
  vector_store: boolean;
  llm_provider: string;
}

export interface MetricsResponse {
  claims_today: number;
  stp_rate: number;
  fraud_hit_rate: number;
  avg_decision_time_ms: number;
  decision_mix: {
    approve: number;
    review: number;
    reject: number;
  };
  top_fraud_scenarios: { name: string; count: number }[];
  top_policy_exclusions: { name: string; count: number }[];
}

// Form/Input types
export interface CreateClaimInput {
  customer_name: string;
  customer_email: string;
  policy_number: string;
  claim_type: string;
  amount: number;
  currency?: string;
  incident_date: string;
  incident_location: string;
  description: string;
}

export interface IntakeFormData {
  policy_number: string;
  incident_date: string;
  incident_location: string;
  claim_type: string;
  amount_estimate: number;
  description: string;
  attachments?: File[];
}
