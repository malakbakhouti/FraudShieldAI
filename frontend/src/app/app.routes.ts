import { Routes } from '@angular/router';
import { HomeComponent } from './components/home/home.component';
import { ShellComponent } from './components/shell/shell.component';
import { DashboardPageComponent } from './components/dashboard-page/dashboard-page.component';
import { TransactionsPageComponent } from './components/transactions-page/transactions-page.component';
import { AlertsPageComponent } from './components/alerts-page/alerts-page.component';
import { PlaceholderPageComponent } from './components/placeholder-page/placeholder-page.component';

export const routes: Routes = [
  { path: '', component: HomeComponent },
  {
    path: 'app',
    component: ShellComponent,
    children: [
      { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
      { path: 'dashboard', component: DashboardPageComponent },
      { path: 'transactions', component: TransactionsPageComponent },
      { path: 'alerts', component: AlertsPageComponent },
      { path: 'models', component: PlaceholderPageComponent, data: { title: 'Models', description: 'Model performance metrics and version history will appear here.' } },
      { path: 'rules', component: PlaceholderPageComponent, data: { title: 'Rules', description: 'Configure automated fraud detection rules.' } },
      { path: 'reports', component: PlaceholderPageComponent, data: { title: 'Reports', description: 'Generate and export fraud analysis reports.' } },
      { path: 'settings', component: PlaceholderPageComponent, data: { title: 'Settings', description: 'Manage your account and notification preferences.' } },
    ]
  },
];
