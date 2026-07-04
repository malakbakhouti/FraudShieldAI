import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../services/auth.service';
import { SettingsService } from '../../services/settings.service';

@Component({
  selector: 'app-settings-page',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './settings-page.component.html',
  styleUrl: './settings-page.component.scss'
})
export class SettingsPageComponent {
  currentPassword = '';
  newPassword = '';
  confirmPassword = '';
  passwordError = signal<string | null>(null);
  passwordSuccess = signal<string | null>(null);

  alertThreshold = 70;

  notifyEmail = true;
  notifyHighRiskOnly = true;
  notifyDailySummary = false;

  constructor(public auth: AuthService, private settingsService: SettingsService) {}

  submitPasswordChange(): void {
    this.passwordError.set(null);
    this.passwordSuccess.set(null);

    if (this.newPassword !== this.confirmPassword) {
      this.passwordError.set('New password and confirmation do not match.');
      return;
    }

    if (this.newPassword.length < 6) {
      this.passwordError.set('New password must be at least 6 characters.');
      return;
    }

    this.settingsService.changePassword(this.currentPassword, this.newPassword).subscribe({
      next: () => {
        this.passwordSuccess.set('Password updated successfully.');
        this.currentPassword = '';
        this.newPassword = '';
        this.confirmPassword = '';
      },
      error: (err) => {
        this.passwordError.set(err.error?.detail || 'Failed to update password.');
      }
    });
  }
}
