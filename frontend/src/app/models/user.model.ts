export interface AuthResponse {
  access_token: string;
  token_type: string;
  email: string;
  full_name: string | null;
  role: 'admin' | 'analyst';
}
