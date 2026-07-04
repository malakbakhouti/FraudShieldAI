import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { TransactionService } from '../../services/transaction.service';
import { TransactionDetail } from '../../models/transaction.model';

const COUNTRIES = ['France', 'Germany', 'Spain', 'United States', 'United Kingdom', 'Morocco', 'Italy', 'Netherlands'];

@Component({
  selector: 'app-transaction-detail-page',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './transaction-detail-page.component.html',
  styleUrl: './transaction-detail-page.component.scss'
})
export class TransactionDetailPageComponent implements OnInit {
  transaction = signal<TransactionDetail | null>(null);
  loading = signal(true);
  notFound = signal(false);

  cardMask = '';
  country = '';

  constructor(private route: ActivatedRoute, private txService: TransactionService) {}

  ngOnInit(): void {
    const id = Number(this.route.snapshot.paramMap.get('id'));

    this.txService.getDetail(id).subscribe({
      next: (tx) => {
        this.transaction.set(tx);
        this.loading.set(false);
        this.cardMask = `•••• ${1000 + (id % 9000)}`;
        this.country = COUNTRIES[id % COUNTRIES.length];
      },
      error: () => {
        this.notFound.set(true);
        this.loading.set(false);
      }
    });
  }

  get topFeatures(): { key: string; value: number }[] {
    const tx = this.transaction();
    if (!tx || !tx.features) return [];
    return Object.entries(tx.features)
      .filter(([key]) => key.startsWith('V'))
      .map(([key, value]) => ({ key, value: Number(value) }))
      .sort((a, b) => Math.abs(b.value) - Math.abs(a.value))
      .slice(0, 8);
  }

  riskLevel(prob: number): 'high' | 'medium' | 'low' {
    if (prob > 0.5) return 'high';
    if (prob > 0.2) return 'medium';
    return 'low';
  }
}
