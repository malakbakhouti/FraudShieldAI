import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TransactionService } from '../../services/transaction.service';

interface ImportResult {
  total_imported: number;
  frauds_detected: number;
  errors: number;
  fraud_rate: number;
}

@Component({
  selector: 'app-import-page',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './import-page.component.html',
  styleUrl: './import-page.component.scss'
})
export class ImportPageComponent {
  selectedFile = signal<File | null>(null);
  uploading = signal(false);
  result = signal<ImportResult | null>(null);
  error = signal<string | null>(null);
  dragging = signal(false);

  constructor(private txService: TransactionService) {}

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files[0]) {
      this.setFile(input.files[0]);
    }
  }

  onDrop(event: DragEvent): void {
    event.preventDefault();
    this.dragging.set(false);
    const file = event.dataTransfer?.files?.[0];
    if (file) this.setFile(file);
  }

  onDragOver(event: DragEvent): void {
    event.preventDefault();
    this.dragging.set(true);
  }

  onDragLeave(): void {
    this.dragging.set(false);
  }

  setFile(file: File): void {
    this.error.set(null);
    this.result.set(null);
    if (!file.name.endsWith('.csv')) {
      this.error.set('Please select a .csv file');
      return;
    }
    this.selectedFile.set(file);
  }

  upload(): void {
    const file = this.selectedFile();
    if (!file) return;

    this.uploading.set(true);
    this.error.set(null);

    this.txService.importCsv(file).subscribe({
      next: (res) => {
        this.result.set(res);
        this.uploading.set(false);
        this.selectedFile.set(null);
      },
      error: (err) => {
        this.error.set(err.error?.detail || 'Import failed. Please check your file format.');
        this.uploading.set(false);
      }
    });
  }

  reset(): void {
    this.selectedFile.set(null);
    this.result.set(null);
    this.error.set(null);
  }
}
