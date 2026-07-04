import { Component, OnDestroy, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TransactionService } from '../../services/transaction.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss'
})
export class DashboardComponent implements OnInit, OnDestroy {
  constructor(public txService: TransactionService) {}

  ngOnInit(): void {
    this.txService.refreshStats();
    this.txService.connectStream();
  }

  ngOnDestroy(): void {
    this.txService.disconnectStream();
  }

  formatTime(iso: string): string {
    return new Date(iso).toLocaleTimeString('fr-FR');
  }
}
