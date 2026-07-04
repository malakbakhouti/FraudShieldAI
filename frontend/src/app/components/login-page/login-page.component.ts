import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-login-page',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './login-page.component.html',
  styleUrl: './login-page.component.scss'
})
export class LoginPageComponent {
  mode = signal<'login' | 'signup'>('login');
  email = '';
  password = '';
  fullName = '';
  loading = signal(false);
  error = signal<string | null>(null);

  constructor(private auth: AuthService, private router: Router) {}

  toggleMode(): void {
    this.mode.set(this.mode() === 'login' ? 'signup' : 'login');
    this.error.set(null);
  }

  submit(): void {
    this.error.set(null);
    this.loading.set(true);

    const request = this.mode() === 'login'
      ? this.auth.login(this.email, this.password)
      : this.auth.signup(this.email, this.password, this.fullName);

    request.subscribe({
      next: (res) => {
        this.auth.setSession(res);
        this.loading.set(false);
        this.router.navigate(['/app/dashboard']);
      },
      error: (err) => {
        this.error.set(err.error?.detail || 'Something went wrong. Please try again.');
        this.loading.set(false);
      }
    });
  }
}
