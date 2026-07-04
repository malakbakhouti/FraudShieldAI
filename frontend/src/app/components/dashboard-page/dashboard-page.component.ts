import { Component, OnDestroy, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TransactionService } from '../../services/transaction.service';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-dashboard-page',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './dashboard-page.component.html',
  styleUrl: './dashboard-page.component.scss'
})
export class DashboardPageComponent implements OnInit, OnDestroy {
  chartRange: 'daily' | 'weekly' | 'monthly' = 'daily';

  private chartDatasets = {
    daily: {
      labels: ['May 12', 'May 13', 'May 14', 'May 15', 'May 16', 'May 17', 'May 18'],
      values: [1000, 1400, 1100, 1900, 1250, 2050, 2900],
      max: 3000
    },
    weekly: {
      labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
      values: [6200, 8100, 7400, 9800],
      max: 10000
    },
    monthly: {
      labels: ['Feb', 'Mar', 'Apr', 'May', 'Jun'],
      values: [21000, 25400, 23100, 29800, 32500],
      max: 35000
    }
  };

  onRangeChange(event: Event): void {
    this.chartRange = (event.target as HTMLSelectElement).value as 'daily' | 'weekly' | 'monthly';
  }

  get chartLabels(): string[] {
    return this.chartDatasets[this.chartRange].labels;
  }

  get chartDots(): { x: number; y: number }[] {
    const { values, max } = this.chartDatasets[this.chartRange];
    const step = 400 / (values.length - 1);
    return values.map((v, i) => ({
      x: i * step,
      y: 130 - (v / max) * 120
    }));
  }

  get chartPoints(): string {
    return this.chartDots.map(p => `${p.x},${p.y}`).join(' ');
  }

  get areaPoints(): string {
    const dots = this.chartDots;
    const first = dots[0];
    const last = dots[dots.length - 1];
    return `${first.x},130 ` + dots.map(p => `${p.x},${p.y}`).join(' ') + ` ${last.x},130`;
  }

  allCountries = [
    { name: 'Russia', flag: '🇷🇺', value: 1250 },
    { name: 'Brazil', flag: '🇧🇷', value: 980 },
    { name: 'India', flag: '🇮🇳', value: 874 },
    { name: 'Nigeria', flag: '🇳🇬', value: 645 },
    { name: 'United Kingdom', flag: '🇬🇧', value: 432 },
    { name: 'United States', flag: '🇺🇸', value: 398 },
    { name: 'France', flag: '🇫🇷', value: 312 },
    { name: 'Germany', flag: '🇩🇪', value: 287 },
    { name: 'Mexico', flag: '🇲🇽', value: 254 },
    { name: 'South Africa', flag: '🇿🇦', value: 201 },
    { name: 'Indonesia', flag: '🇮🇩', value: 176 },
    { name: 'Morocco', flag: '🇲🇦', value: 143 },
  ];

  get topCountries() {
    const sorted = [...this.allCountries].sort((a, b) => b.value - a.value);
    const max = sorted[0]?.value || 1;
    return sorted.slice(0, 5).map(c => ({ ...c, max }));
  }

  riskDistribution = { high: 15, medium: 28, low: 57 };

  constructor(public txService: TransactionService) {}

  ngOnInit(): void {
    this.txService.refreshStats();
    this.txService.connectStream();
  }

  ngOnDestroy(): void {
    this.txService.disconnectStream();
  }
}
