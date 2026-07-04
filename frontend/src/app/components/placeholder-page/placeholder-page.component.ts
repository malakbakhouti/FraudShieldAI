import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute } from '@angular/router';

@Component({
  selector: 'app-placeholder-page',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './placeholder-page.component.html',
  styleUrl: './placeholder-page.component.scss'
})
export class PlaceholderPageComponent {
  title = signal('');
  description = signal('');

  constructor(route: ActivatedRoute) {
    this.title.set(route.snapshot.data['title'] ?? 'Coming Soon');
    this.description.set(route.snapshot.data['description'] ?? 'This section is under construction.');
  }
}
