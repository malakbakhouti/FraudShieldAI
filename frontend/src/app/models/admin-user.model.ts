export interface AdminUser {
  id: number;
  email: string;
  full_name: string | null;
  role: 'admin' | 'analyst';
}
