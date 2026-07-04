import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TransactionService } from '../../services/transaction.service';
import { Transaction } from '../../models/transaction.model';

interface DayStat {
  label: string;
  total: number;
  fraud: number;
}

@Component({
  selector: 'app-reports-page',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './reports-page.component.html',
  styleUrl: './reports-page.component.scss'
})
export class ReportsPageComponent implements OnInit {
  loading = signal(true);
  transactions = signal<Transaction[]>([]);
  dayStats = signal<DayStat[]>([]);

  totalTransactions = 0;
  totalFraud = 0;
  detectionRate = 0;
  avgAmount = 0;

  constructor(private txService: TransactionService) {}

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.loading.set(true);
    this.txService.loadHistory(500).subscribe(data => {
      this.transactions.set(data);
      this.computeStats(data);
      this.loading.set(false);
    });
  }

  private computeStats(data: Transaction[]): void {
    this.totalTransactions = data.length;
    this.totalFraud = data.filter(t => t.is_fraud).length;
    this.detectionRate = this.totalTransactions
      ? (this.totalFraud / this.totalTransactions) * 100
      : 0;
    this.avgAmount = this.totalTransactions
      ? data.reduce((sum, t) => sum + t.amount, 0) / this.totalTransactions
      : 0;

    const grouped = new Map<string, DayStat>();
    for (const tx of data) {
      const date = new Date(tx.created_at);
      const label = date.toLocaleDateString('en-GB', { day: '2-digit', month: 'short' });
      if (!grouped.has(label)) {
        grouped.set(label, { label, total: 0, fraud: 0 });
      }
      const entry = grouped.get(label)!;
      entry.total += 1;
      if (tx.is_fraud) entry.fraud += 1;
    }

    this.dayStats.set(Array.from(grouped.values()).slice(-7));
  }

  maxDayTotal(): number {
    const stats = this.dayStats();
    return stats.length ? Math.max(...stats.map(d => d.total)) : 1;
  }

  exportCsv(): void {
    const rows = this.transactions().map(t =>
      `${t.id},${t.amount},${t.fraud_probability},${t.is_fraud},${t.created_at}`
    );
    const csv = 'id,amount,fraud_probability,is_fraud,created_at\n' + rows.join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'fraud_report.csv';
    a.click();
    URL.revokeObjectURL(url);
  }
}
