import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { UserAdminService } from '../../services/user-admin.service';
import { AdminUser } from '../../models/admin-user.model';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-users-page',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './users-page.component.html',
  styleUrl: './users-page.component.scss'
})
export class UsersPageComponent implements OnInit {
  users = signal<AdminUser[]>([]);
  loading = signal(true);
  error = signal<string | null>(null);

  showForm = signal(false);
  editingId = signal<number | null>(null);

  formEmail = '';
  formPassword = '';
  formFullName = '';
  formRole: 'admin' | 'analyst' = 'analyst';

  constructor(private userAdmin: UserAdminService, public auth: AuthService) {}

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.loading.set(true);
    this.error.set(null);
    this.userAdmin.list().subscribe({
      next: (data) => {
        this.users.set(data);
        this.loading.set(false);
      },
      error: (err) => {
        this.error.set(err.error?.detail || 'Failed to load users.');
        this.loading.set(false);
      }
    });
  }

  openCreateForm(): void {
    this.showForm.set(true);
    this.editingId.set(null);
    this.formEmail = '';
    this.formPassword = '';
    this.formFullName = '';
    this.formRole = 'analyst';
  }

  openEditForm(user: AdminUser): void {
    this.showForm.set(true);
    this.editingId.set(user.id);
    this.formEmail = user.email;
    this.formPassword = '';
    this.formFullName = user.full_name || '';
    this.formRole = user.role;
  }

  isEditingSelf(): boolean {
    return this.auth.currentUser()?.email === this.formEmail;
  }

  cancelForm(): void {
    this.showForm.set(false);
    this.editingId.set(null);
  }

  submitForm(): void {
    const id = this.editingId();

    if (id === null) {
      this.userAdmin.create(this.formEmail, this.formPassword, this.formFullName, this.formRole).subscribe({
        next: () => {
          this.showForm.set(false);
          this.load();
        },
        error: (err) => this.error.set(err.error?.detail || 'Failed to create user.')
      });
    } else {
      this.userAdmin.update(id, this.formFullName, this.formRole).subscribe({
        next: () => {
          this.showForm.set(false);
          this.load();
        },
        error: (err) => this.error.set(err.error?.detail || 'Failed to update user.')
      });
    }
  }

  deleteUser(user: AdminUser): void {
    if (!confirm(`Delete user ${user.email}? This cannot be undone.`)) return;

    this.userAdmin.delete(user.id).subscribe({
      next: () => this.load(),
      error: (err) => this.error.set(err.error?.detail || 'Failed to delete user.')
    });
  }
}
