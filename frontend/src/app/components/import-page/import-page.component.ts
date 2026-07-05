import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TransactionService } from '../../services/transaction.service';

interface ImportResult {
  total_imported: number;
  frauds_detected: number;
  errors: number;
  fraud_rate: number;
}

interface ImportHistoryItem {
  id: number;
  filename: string;
  imported_by_email: string;
  total_records: number;
  frauds_detected: number;
  errors: number;
  status: string;
  created_at: string;
}

@Component({
  selector: 'app-import-page',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './import-page.component.html',
  styleUrl: './import-page.component.scss'
})
export class ImportPageComponent implements OnInit {
  selectedFile = signal<File | null>(null);
  dragging = signal(false);

  previewColumns = signal<string[]>([]);
  previewRows = signal<Record<string, any>[]>([]);
  previewTotalRows = signal(0);
  previewLoading = signal(false);
  previewError = signal<string | null>(null);

  uploading = signal(false);
  uploadProgress = signal(0);
  result = signal<ImportResult | null>(null);
  uploadError = signal<string | null>(null);

  history = signal<ImportHistoryItem[]>([]);
  historyLoading = signal(true);

  constructor(private txService: TransactionService) {}

  ngOnInit(): void {
    this.loadHistory();
  }

  loadHistory(): void {
    this.historyLoading.set(true);
    this.txService.getImportHistory().subscribe({
      next: (data) => {
        this.history.set(data);
        this.historyLoading.set(false);
      },
      error: () => this.historyLoading.set(false)
    });
  }

  onDrop(event: DragEvent): void {
    event.preventDefault();
    this.dragging.set(false);
    const file = event.dataTransfer?.files?.[0];
    if (file) this.handleFile(file);
  }

  onDragOver(event: DragEvent): void {
    event.preventDefault();
    this.dragging.set(true);
  }

  onDragLeave(): void {
    this.dragging.set(false);
  }

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files[0]) {
      this.handleFile(input.files[0]);
    }
  }

  private handleFile(file: File): void {
    this.previewError.set(null);
    this.result.set(null);
    this.uploadError.set(null);

    if (!file.name.endsWith('.csv')) {
      this.previewError.set('Please select a .csv file.');
      return;
    }

    this.selectedFile.set(file);
    this.previewLoading.set(true);

    this.txService.previewCsv(file).subscribe({
      next: (res) => {
        this.previewColumns.set(res.columns);
        this.previewRows.set(res.preview);
        this.previewTotalRows.set(res.total_rows);
        this.previewLoading.set(false);
      },
      error: (err) => {
        this.previewError.set(err.error?.detail || 'Could not preview file.');
        this.previewLoading.set(false);
        this.selectedFile.set(null);
      }
    });
  }

  cancel(): void {
    this.selectedFile.set(null);
    this.previewColumns.set([]);
    this.previewRows.set([]);
    this.previewError.set(null);
    this.result.set(null);
    this.uploadError.set(null);
  }

  confirmImport(): void {
    const file = this.selectedFile();
    if (!file) return;

    this.uploading.set(true);
    this.uploadProgress.set(0);
    this.uploadError.set(null);

    const interval = setInterval(() => {
      this.uploadProgress.update(p => Math.min(p + 10, 90));
    }, 150);

    this.txService.importCsv(file).subscribe({
      next: (res) => {
        clearInterval(interval);
        this.uploadProgress.set(100);
        setTimeout(() => {
          this.result.set(res);
          this.uploading.set(false);
          this.selectedFile.set(null);
          this.previewColumns.set([]);
          this.previewRows.set([]);
          this.loadHistory();
        }, 300);
      },
      error: (err) => {
        clearInterval(interval);
        this.uploadError.set(err.error?.detail || 'Import failed. Please check your file format.');
        this.uploading.set(false);
      }
    });
  }

  reset(): void {
    this.result.set(null);
    this.cancel();
  }
}
