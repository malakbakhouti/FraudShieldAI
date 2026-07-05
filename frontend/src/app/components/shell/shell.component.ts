import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-shell',
  standalone: true,
  imports: [CommonModule, RouterLink, RouterLinkActive, RouterOutlet],
  templateUrl: './shell.component.html',
  styleUrl: './shell.component.scss'
})
export class ShellComponent {
  constructor(public auth: AuthService) {}

  navItems = [
    { label: 'Dashboard', path: '/app/dashboard', adminOnly: false },
    { label: 'Transactions', path: '/app/transactions', adminOnly: false },
    { label: 'Alerts', path: '/app/alerts', adminOnly: false },
    { label: 'Reports', path: '/app/reports', adminOnly: false },
    { label: 'Users', path: '/app/users', adminOnly: true },
    { label: 'Models', path: '/app/models', adminOnly: true },
    { label: 'Import Dataset', path: '/app/import', adminOnly: false },
    { label: 'Settings', path: '/app/settings', adminOnly: false },
  ];
}
