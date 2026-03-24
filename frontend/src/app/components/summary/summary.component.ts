import { Component, Input, OnChanges, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService, SummaryResponse } from '../../services/api.service';

@Component({
  selector: 'app-summary',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './summary.component.html',
  styleUrl: './summary.component.css',
})
export class SummaryComponent implements OnChanges {
  @Input() paperId = '';

  activeLevel: 'beginner' | 'technical' = 'beginner';
  summaryText = '';
  isLoading = false;
  hasLoaded = false;

  constructor(private api: ApiService) {}

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['paperId'] && this.paperId) {
      this.loadSummary();
    }
  }

  switchLevel(level: 'beginner' | 'technical'): void {
    this.activeLevel = level;
    this.loadSummary();
  }

  loadSummary(): void {
    if (!this.paperId) return;
    this.isLoading = true;
    this.api.getSummary(this.paperId, this.activeLevel).subscribe({
      next: (res: SummaryResponse) => {
        this.summaryText = res.summary;
        this.isLoading = false;
        this.hasLoaded = true;
      },
      error: () => {
        this.summaryText = 'Failed to generate summary. Please try again.';
        this.isLoading = false;
      },
    });
  }
}
