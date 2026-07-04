export interface Transaction {
  id: number;
  amount: number;
  fraud_probability: number;
  is_fraud: boolean;
  created_at: string;
}

export interface TransactionStats {
  total_transactions: number;
  total_frauds: number;
  fraud_rate: number;
  avg_amount: number;
}
