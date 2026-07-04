import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { AdminUser } from '../models/admin-user.model';
import { AuthService } from './auth.service';

@Injectable({ providedIn: 'root' })
export class UserAdminService {
  private readonly apiUrl = 'http://localhost:8000/api/users';

  constructor(private http: HttpClient, private auth: AuthService) {}

  private authHeaders(): HttpHeaders {
    return new HttpHeaders({
      Authorization: `Bearer ${this.auth.getToken()}`
    });
  }

  list() {
    return this.http.get<AdminUser[]>(`${this.apiUrl}/`, { headers: this.authHeaders() });
  }

  create(email: string, password: string, full_name: string, role: string) {
    return this.http.post<AdminUser>(`${this.apiUrl}/`, { email, password, full_name, role }, { headers: this.authHeaders() });
  }

  update(id: number, full_name: string, role: string) {
    return this.http.put<AdminUser>(`${this.apiUrl}/${id}`, { full_name, role }, { headers: this.authHeaders() });
  }

  delete(id: number) {
    return this.http.delete(`${this.apiUrl}/${id}`, { headers: this.authHeaders() });
  }
}
