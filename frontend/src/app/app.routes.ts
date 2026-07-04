import { Routes } from '@angular/router';
import { HomeComponent } from './components/home/home.component';
import { ShellComponent } from './components/shell/shell.component';
import { DashboardPageComponent } from './components/dashboard-page/dashboard-page.component';
import { TransactionsPageComponent } from './components/transactions-page/transactions-page.component';
import { TransactionDetailPageComponent } from './components/transaction-detail-page/transaction-detail-page.component';
import { AlertsPageComponent } from './components/alerts-page/alerts-page.component';
import { PlaceholderPageComponent } from './components/placeholder-page/placeholder-page.component';
import { ReportsPageComponent } from './components/reports-page/reports-page.component';
import { ModelsPageComponent } from './components/models-page/models-page.component';
import { UsersPageComponent } from './components/users-page/users-page.component';
import { SettingsPageComponent } from './components/settings-page/settings-page.component';
import { LiveDetectionPageComponent } from './components/live-detection-page/live-detection-page.component';
import { LoginPageComponent } from './components/login-page/login-page.component';
import { authGuard } from './guards/auth.guard';
import { adminGuard } from './guards/admin.guard';

export const routes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'login', component: LoginPageComponent },
  {
    path: 'app',
    component: ShellComponent,
    canActivate: [authGuard],
    children: [
      { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
      { path: 'dashboard', component: DashboardPageComponent },
      { path: 'live-detection', component: LiveDetectionPageComponent },
      { path: 'transactions', component: TransactionsPageComponent },
      { path: 'transactions/:id', component: TransactionDetailPageComponent },
      { path: 'alerts', component: AlertsPageComponent },
      { path: 'models', component: ModelsPageComponent, canActivate: [adminGuard] },
      { path: 'rules', component: PlaceholderPageComponent, data: { title: 'Rules', description: 'Configure automated fraud detection rules.' } },
      { path: 'reports', component: ReportsPageComponent },
      { path: 'settings', component: SettingsPageComponent },
      { path: 'users', component: UsersPageComponent, canActivate: [adminGuard] },
    ]
  },
];
