import { Component, OnDestroy, OnInit, signal } from '@angular/core';
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
  dailySummary = signal<{ label: string; value: number }[]>([]);

  private groupByDay(): { label: string; value: number }[] {
    return this.dailySummary();
  }

  get chartLabels(): string[] {
    return this.groupByDay().map(d => d.label);
  }

  get chartMax(): number {
    const grouped = this.groupByDay();
    const rawMax = grouped.length ? Math.max(...grouped.map(d => d.value)) : 0;

    if (rawMax === 0) {
      return 1;
    }

    const magnitude = Math.pow(10, Math.floor(Math.log10(rawMax)));
    return Math.ceil(rawMax / magnitude) * magnitude;
  }

  private formatAxisValue(v: number): string {
    if (v >= 1000) {
      return (v / 1000).toFixed(v % 1000 === 0 ? 0 : 1) + 'K';
    }
    if (Number.isInteger(v)) {
      return v.toString();
    }
    return v.toFixed(1);
  }

  get chartYLabels(): string[] {
    const max = this.chartMax;
    const values = [max, max * 0.66, max * 0.33, 0];
    return values.map(v => this.formatAxisValue(v));
  }

  get chartDots(): { x: number; y: number }[] {
    const grouped = this.groupByDay();
    if (grouped.length === 0) return [];

    const max = this.chartMax;
    const step = grouped.length > 1 ? 400 / (grouped.length - 1) : 0;

    return grouped.map((d, i) => ({
      x: grouped.length > 1 ? i * step : 200,
      y: 130 - (d.value / max) * 120
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

  get chartDotsOffset(): { x: number; y: number }[] {
    return this.chartDots.map(p => ({ x: p.x + 36, y: p.y }));
  }

  get chartXLabelsPositioned(): { label: string; x: number }[] {
    const dots = this.chartDotsOffset;
    const labels = this.chartLabels;
    return labels.map((label, i) => ({ label, x: dots[i]?.x ?? 36 }));
  }

  get chartPointsOffset(): string {
    return this.chartDotsOffset.map(p => `${p.x},${p.y}`).join(' ');
  }

  get areaPointsOffset(): string {
    const dots = this.chartDotsOffset;
    if (dots.length === 0) return '';
    const first = dots[0];
    const last = dots[dots.length - 1];
    return `${first.x},130 ` + dots.map(p => `${p.x},${p.y}`).join(' ') + ` ${last.x},130`;
  }

  private countryFlags: Record<string, string> = {
    'France': '🇫🇷', 'Germany': '🇩🇪', 'United States': '🇺🇸', 'United Kingdom': '🇬🇧',
    'Spain': '🇪🇸', 'Italy': '🇮🇹', 'Morocco': '🇲🇦', 'Brazil': '🇧🇷',
    'Russia': '🇷🇺', 'India': '🇮🇳', 'Nigeria': '🇳🇬', 'Indonesia': '🇮🇩'
  };

  topCountries = signal<{ name: string; flag: string; value: number; max: number }[]>([]);
  riskDistribution = signal({ high: 0, medium: 0, low: 100 });

  constructor(public txService: TransactionService) {}

  ngOnInit(): void {
    this.txService.refreshStats();
    this.txService.connectStream();
    this.txService.getDailySummary().subscribe(data => {
      this.dailySummary.set(data.map(d => ({ label: d.day, value: d.frauds })));
    });

    this.txService.getTopCountries().subscribe(data => {
      const max = Math.max(...data.map(d => d.value), 1);
      this.topCountries.set(data.map(d => ({
        name: d.name,
        flag: this.countryFlags[d.name] || '🏳',
        value: d.value,
        max
      })));
    });

    this.txService.getRiskDistribution().subscribe(data => {
      this.riskDistribution.set(data);
    });
  }

  ngOnDestroy(): void {
    this.txService.disconnectStream();
  }
}
