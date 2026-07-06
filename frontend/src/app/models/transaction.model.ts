export interface Transaction {
  id: number;
  amount: number;
  fraud_probability: number;
  is_fraud: boolean;
  created_at: string;
}

export interface ExplanationFactor {
  factor_name: string;
  score: number;
  weight: number;
  weighted_score: number;
  confidence: number;
  details: string;
}

export interface ExplanationSection {
  score: number;
  severity: 'low' | 'medium' | 'high';
  factors: ExplanationFactor[];
  details: string[];
}

export interface ExplanationReason {
  title: string;
  severity: 'low' | 'medium' | 'high';
  score: number;
  details: string;
}

export interface Explanation {
  overall_risk: {
    score: number;
    severity: 'low' | 'medium' | 'high';
  };
  country: ExplanationSection;
  reasons: ExplanationReason[];
}

export interface TransactionDetail extends Transaction {
  country?: string;
  features: Record<string, number>;
  explanation: Explanation | null;
}

export interface TransactionStats {
  total_transactions: number;
  total_frauds: number;
  fraud_rate: number;
  avg_amount: number;
}
