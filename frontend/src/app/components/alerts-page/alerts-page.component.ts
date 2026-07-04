import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TransactionService } from '../../services/transaction.service';
import { Transaction } from '../../models/transaction.model';

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
  reviewedIds = signal<Set<number>>(new Set());

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

  markReviewed(id: number): void {
    const current = new Set(this.reviewedIds());
    current.add(id);
    this.reviewedIds.set(current);
  }

  isReviewed(id: number): boolean {
    return this.reviewedIds().has(id);
  }
}
