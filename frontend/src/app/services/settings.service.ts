import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { AuthService } from './auth.service';

@Injectable({ providedIn: 'root' })
export class SettingsService {
  private readonly apiUrl = 'http://localhost:8000/api/settings';

  constructor(private http: HttpClient, private auth: AuthService) {}

  private authHeaders(): HttpHeaders {
    return new HttpHeaders({
      Authorization: `Bearer ${this.auth.getToken()}`
    });
  }

  changePassword(currentPassword: string, newPassword: string) {
    return this.http.put<{ detail: string }>(
      `${this.apiUrl}/password`,
      { current_password: currentPassword, new_password: newPassword },
      { headers: this.authHeaders() }
    );
  }
}
