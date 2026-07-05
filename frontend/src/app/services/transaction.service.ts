import { Injectable, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Transaction, TransactionStats, TransactionDetail } from '../models/transaction.model';

@Injectable({ providedIn: 'root' })
export class TransactionService {
  private readonly apiUrl = 'http://localhost:8000/api/transactions';
  private readonly wsUrl = 'ws://localhost:8000/ws/transactions';
  private socket?: WebSocket;

  transactions = signal<Transaction[]>([]);
  stats = signal<TransactionStats | null>(null);
  connected = signal(false);

  constructor(private http: HttpClient) {}

  connectStream(maxItems = 30): void {
    this.socket = new WebSocket(this.wsUrl);

    this.socket.onopen = () => this.connected.set(true);
    this.socket.onclose = () => this.connected.set(false);
    this.socket.onerror = () => this.connected.set(false);

    this.socket.onmessage = (event) => {
      const tx: Transaction = JSON.parse(event.data);
      this.transactions.update(list => [tx, ...list].slice(0, maxItems));
      this.refreshStats();
    };
  }

  disconnectStream(): void {
    this.socket?.close();
  }

  refreshStats(): void {
    this.http.get<TransactionStats>(`${this.apiUrl}/stats`)
      .subscribe(stats => this.stats.set(stats));
  }

  loadHistory(limit = 50) {
    return this.http.get<Transaction[]>(`${this.apiUrl}/?limit=${limit}`);
  }

  getDetail(id: number) {
    return this.http.get<TransactionDetail>(`${this.apiUrl}/${id}`);
  }

  getDailySummary() {
    return this.http.get<{ day: string; frauds: number; total: number }[]>(`${this.apiUrl}/daily-summary`);
  }

  getTopCountries() {
    return this.http.get<{ name: string; value: number }[]>(`${this.apiUrl}/analytics/top-countries`);
  }

  getRiskDistribution() {
    return this.http.get<{ high: number; medium: number; low: number }>(`${this.apiUrl}/analytics/risk-distribution`);
  }

  importCsv(file: File) {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post<{
      total_imported: number;
      frauds_detected: number;
      errors: number;
      fraud_rate: number;
    }>('http://localhost:8000/api/import/csv', formData, {
      headers: { Authorization: `Bearer ${localStorage.getItem('fraudshield_token')}` }
    });
  }

  previewCsv(file: File) {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post<{
      columns: string[];
      total_rows: number;
      preview: Record<string, any>[];
    }>('http://localhost:8000/api/import/preview', formData);
  }

  getImportHistory() {
    return this.http.get<{
      id: number;
      filename: string;
      imported_by_email: string;
      total_records: number;
      frauds_detected: number;
      errors: number;
      status: string;
      created_at: string;
    }[]>('http://localhost:8000/api/import/history', {
      headers: { Authorization: `Bearer ${localStorage.getItem('fraudshield_token')}` }
    });
  }
}
