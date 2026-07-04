import { Injectable, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Transaction, TransactionStats } from '../models/transaction.model';

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
}
