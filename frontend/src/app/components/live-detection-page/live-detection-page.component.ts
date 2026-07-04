import { Component, OnDestroy, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { TransactionService } from '../../services/transaction.service';

@Component({
  selector: 'app-live-detection-page',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './live-detection-page.component.html',
  styleUrl: './live-detection-page.component.scss'
})
export class LiveDetectionPageComponent implements OnInit, OnDestroy {
  constructor(public txService: TransactionService) {}

  ngOnInit(): void {
    this.txService.refreshStats();
    this.txService.connectStream();
  }

  ngOnDestroy(): void {
    this.txService.disconnectStream();
  }
}
