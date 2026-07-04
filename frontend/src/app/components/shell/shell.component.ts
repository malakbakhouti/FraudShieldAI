import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-shell',
  standalone: true,
  imports: [CommonModule, RouterLink, RouterLinkActive, RouterOutlet],
  templateUrl: './shell.component.html',
  styleUrl: './shell.component.scss'
})
export class ShellComponent {
  navItems = [
    { label: 'Dashboard', path: '/app/dashboard' },
    { label: 'Transactions', path: '/app/transactions' },
    { label: 'Alerts', path: '/app/alerts' },
    { label: 'Models', path: '/app/models' },
    { label: 'Rules', path: '/app/rules' },
    { label: 'Reports', path: '/app/reports' },
    { label: 'Settings', path: '/app/settings' },
  ];
}
