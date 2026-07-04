import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TransactionService } from '../../services/transaction.service';
import { Transaction } from '../../models/transaction.model';

export type AlertStatus = 'pending' | 'legitimate' | 'confirmed' | 'closed';

@Component({
  selector: 'app-alerts-page',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './alerts-page.component.html',
  styleUrl: './alerts-page.component.scss'
})
export class AlertsPageComponent implements OnInit {
  alerts = signal<Transaction[]>([]);
  loading = signal(true);
  statusMap = signal<Map<number, AlertStatus>>(new Map());

  constructor(private txService: TransactionService) {}

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.loading.set(true);
    this.txService.loadHistory(100).subscribe(data => {
      this.alerts.set(data.filter(t => t.is_fraud));
      this.loading.set(false);
    });
  }

  setStatus(id: number, status: AlertStatus): void {
    const current = new Map(this.statusMap());
    current.set(id, status);
    this.statusMap.set(current);
  }

  getStatus(id: number): AlertStatus {
    return this.statusMap().get(id) ?? 'pending';
  }
}
