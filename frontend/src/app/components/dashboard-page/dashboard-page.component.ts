import { Component, OnDestroy, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TransactionService } from '../../services/transaction.service';

@Component({
  selector: 'app-dashboard-page',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './dashboard-page.component.html',
  styleUrl: './dashboard-page.component.scss'
})
export class DashboardPageComponent implements OnInit, OnDestroy {
  constructor(public txService: TransactionService) {}

  ngOnInit(): void {
    this.txService.refreshStats();
    this.txService.connectStream();
  }

  ngOnDestroy(): void {
    this.txService.disconnectStream();
  }
}
