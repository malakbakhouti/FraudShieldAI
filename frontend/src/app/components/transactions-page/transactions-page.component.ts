import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { TransactionService } from '../../services/transaction.service';
import { Transaction } from '../../models/transaction.model';

@Component({
  selector: 'app-transactions-page',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './transactions-page.component.html',
  styleUrl: './transactions-page.component.scss'
})
export class TransactionsPageComponent implements OnInit {
  transactions = signal<Transaction[]>([]);
  statusFilter = signal<'all' | 'fraud' | 'normal'>('all');
  loading = signal(true);

  constructor(private txService: TransactionService) {}

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.loading.set(true);
    this.txService.loadHistory(100).subscribe(data => {
      this.transactions.set(data);
      this.loading.set(false);
    });
  }

  get filtered(): Transaction[] {
    const filter = this.statusFilter();
    const list = this.transactions();
    if (filter === 'fraud') return list.filter(t => t.is_fraud);
    if (filter === 'normal') return list.filter(t => !t.is_fraud);
    return list;
  }

  setFilter(f: 'all' | 'fraud' | 'normal'): void {
    this.statusFilter.set(f);
  }
}
