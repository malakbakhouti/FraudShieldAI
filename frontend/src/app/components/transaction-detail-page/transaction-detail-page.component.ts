import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { TransactionService } from '../../services/transaction.service';
import { TransactionDetail, ExplanationFactor } from '../../models/transaction.model';

interface CountryAnalysis {
  country: string;
  fraudRate: string;
  globalRate: string;
  relativeRisk: string;
  sampleSize: string;
  trend: string;
}

interface TimelineStep {
  title: string;
  description: string;
}

const FACTOR_DISPLAY_NAMES: Record<string, string> = {
  CountryRateFactor: 'Country Fraud Rate',
  SampleSizeFactor: 'Historical Sample Size',
  TrendFactor: 'Fraud Trend',
};

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
  animateIn = signal(false);

  cardMask = '';

  constructor(private route: ActivatedRoute, private txService: TransactionService) {}

  ngOnInit(): void {
    const id = Number(this.route.snapshot.paramMap.get('id'));

    this.txService.getDetail(id).subscribe({
      next: (tx) => {
        this.transaction.set(tx);
        this.loading.set(false);
        setTimeout(() => this.animateIn.set(true), 30);
        this.cardMask = `•••• ${1000 + (id % 9000)}`;
      },
      error: () => {
        this.notFound.set(true);
        this.loading.set(false);
      }
    });
  }

  get topFeatures(): { key: string; value: number; abs: number; positive: boolean }[] {
    const tx = this.transaction();
    if (!tx || !tx.features) return [];
    return Object.entries(tx.features)
      .filter(([key]) => key.startsWith('V'))
      .map(([key, value]) => ({
        key,
        value: Number(value),
        abs: Math.abs(Number(value)),
        positive: Number(value) >= 0,
      }))
      .sort((a, b) => b.abs - a.abs)
      .slice(0, 8);
  }

  get maxFeatureAbs(): number {
    return Math.max(...this.topFeatures.map(f => f.abs), 1);
  }

  riskLevel(prob: number): 'high' | 'medium' | 'low' {
    if (prob > 0.5) return 'high';
    if (prob > 0.2) return 'medium';
    return 'low';
  }

  severityClass(severity: string): 'low' | 'medium' | 'high' {
    if (severity === 'high') return 'high';
    if (severity === 'medium') return 'medium';
    return 'low';
  }

  scoreSeverity(score: number): 'low' | 'medium' | 'high' {
    if (score >= 70) return 'high';
    if (score >= 40) return 'medium';
    return 'low';
  }

  factorDisplayName(name: string): string {
    return FACTOR_DISPLAY_NAMES[name] || name;
  }

  weightPercent(weight: number): number {
    return Math.round(weight * 100);
  }

  confidencePercent(confidence: number): number {
    return Math.round(confidence * 100);
  }

  get overallConfidence(): number {
    const factors = this.transaction()?.explanation?.country.factors || [];
    if (factors.length === 0) return 0;
    const totalWeight = factors.reduce((sum, f) => sum + f.weight, 0);
    if (totalWeight <= 0) return 0;
    const weighted = factors.reduce((sum, f) => sum + f.confidence * f.weight, 0);
    return Math.round((weighted / totalWeight) * 100);
  }

  private findFactor(name: string): ExplanationFactor | undefined {
    return this.transaction()?.explanation?.country.factors.find(f => f.factor_name === name);
  }

  get countryAnalysis(): CountryAnalysis | null {
    const tx = this.transaction();
    const exp = tx?.explanation;
    if (!tx || !exp) return null;

    const rateFactor = this.findFactor('CountryRateFactor');
    const trendFactor = this.findFactor('TrendFactor');

    let fraudRate = '-';
    let globalRate = '-';
    let relativeRisk = '-';
    let sampleSize = '-';

    if (rateFactor) {
      const m = rateFactor.details.match(
        /Country fraud rate is ([\d.]+)%\. Global fraud rate is ([\d.]+)%\. Relative risk = ([\d.]+)x .*based on (\d+) transactions/
      );
      if (m) {
        fraudRate = `${m[1]}%`;
        globalRate = `${m[2]}%`;
        relativeRisk = `${m[3]}×`;
        sampleSize = m[4];
      }
    }

    let trend = '-';
    if (trendFactor) {
      const m = trendFactor.details.match(/is (increasing|decreasing|stable) compared/);
      if (m) {
        trend = m[1].charAt(0).toUpperCase() + m[1].slice(1);
      }
    }

    return { country: tx.country || 'Unknown', fraudRate, globalRate, relativeRisk, sampleSize, trend };
  }

  get timelineSteps(): TimelineStep[] {
    const exp = this.transaction()?.explanation;
    const steps: TimelineStep[] = [
      { title: 'Transaction Received', description: 'Incoming transaction captured for real-time analysis.' },
    ];

    if (exp) {
      for (const factor of exp.country.factors) {
        steps.push({
          title: this.factorDisplayName(factor.factor_name),
          description: factor.details,
        });
      }
      steps.push({
        title: 'Overall Risk Score Computed',
        description: `Combined into an overall risk score of ${exp.overall_risk.score}/100 (${exp.overall_risk.severity} risk).`,
      });
    }

    return steps;
  }

  /**
   * Builds a single flowing paragraph (not a bullet list) summarizing the
   * explanation, entirely from the API's own data.
   */
  get aiSummary(): string {
    const tx = this.transaction();
    const exp = tx?.explanation;
    const ca = this.countryAnalysis;
    if (!tx || !exp || !ca) return '';

    const sentences: string[] = [];
    sentences.push(`This transaction originates from ${ca.country}.`);

    const rateFactor = this.findFactor('CountryRateFactor');
    if (rateFactor) {
      const comparison = rateFactor.score >= 70 ? 'significantly above' : rateFactor.score >= 40 ? 'moderately above' : 'in line with';
      sentences.push(`Fraud activity in this country is ${comparison} the global average (${ca.relativeRisk}).`);
    }

    const sampleFactor = this.findFactor('SampleSizeFactor');
    if (sampleFactor) {
      const reliability = sampleFactor.confidence >= 0.75 ? 'reliable' : sampleFactor.confidence >= 0.4 ? 'moderately reliable' : 'based on limited data';
      sentences.push(`Historical statistics are ${reliability} because they are based on ${ca.sampleSize} previous transactions.`);
    }

    const trendFactor = this.findFactor('TrendFactor');
    if (trendFactor && ca.trend !== 'Stable' && ca.trend !== '-') {
      sentences.push(`Recent fraud activity for this country is trending ${ca.trend.toLowerCase()}.`);
    }

    sentences.push(`Overall country risk is classified as ${exp.overall_risk.severity.toUpperCase()}.`);

    return sentences.join(' ');
  }
}
