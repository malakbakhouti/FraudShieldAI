import { Injectable, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { AuthResponse } from '../models/user.model';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly apiUrl = 'http://localhost:8000/api/auth';
  private readonly tokenKey = 'fraudshield_token';

  currentUser = signal<{ email: string; full_name: string | null; role: 'admin' | 'analyst' } | null>(null);

  constructor(private http: HttpClient, private router: Router) {
    this.restoreSession();
  }

  private restoreSession(): void {
    const token = localStorage.getItem(this.tokenKey);
    const email = localStorage.getItem('fraudshield_email');
    const fullName = localStorage.getItem('fraudshield_name');
    const role = localStorage.getItem('fraudshield_role') as 'admin' | 'analyst' | null;
    if (token && email && role) {
      this.currentUser.set({ email, full_name: fullName, role });
    }
  }

  login(email: string, password: string) {
    return this.http.post<AuthResponse>(`${this.apiUrl}/login`, { email, password });
  }

  signup(email: string, password: string, full_name: string) {
    return this.http.post<AuthResponse>(`${this.apiUrl}/signup`, { email, password, full_name });
  }

  setSession(res: AuthResponse): void {
    localStorage.setItem(this.tokenKey, res.access_token);
    localStorage.setItem('fraudshield_email', res.email);
    localStorage.setItem('fraudshield_role', res.role);
    if (res.full_name) localStorage.setItem('fraudshield_name', res.full_name);
    this.currentUser.set({ email: res.email, full_name: res.full_name, role: res.role });
  }

  logout(): void {
    localStorage.removeItem(this.tokenKey);
    localStorage.removeItem('fraudshield_email');
    localStorage.removeItem('fraudshield_name');
    localStorage.removeItem('fraudshield_role');
    this.currentUser.set(null);
    this.router.navigate(['/login']);
  }

  isAdmin(): boolean {
    return this.currentUser()?.role === 'admin';
  }

  isAuthenticated(): boolean {
    return !!localStorage.getItem(this.tokenKey);
  }

  getToken(): string | null {
    return localStorage.getItem(this.tokenKey);
  }
}
