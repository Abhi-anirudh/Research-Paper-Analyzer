import { Component, Input, OnChanges, SimpleChanges, EventEmitter, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService, Section } from '../../services/api.service';

@Component({
  selector: 'app-sections',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './sections.component.html',
  styleUrl: './sections.component.css',
})
export class SectionsComponent implements OnChanges {
  @Input() paperId = '';
  @Input() paperTitle = '';
  @Input() paperAuthors: string[] = [];
  @Input() totalPages = 0;
  @Input() numChunks = 0;
  @Output() sectionSelected = new EventEmitter<string>();

  sections: Section[] = [];
  isLoading = false;
  activeSection = '';
  expandedSection = '';

  constructor(private api: ApiService) {}

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['paperId'] && this.paperId) {
      this.loadSections();
    }
  }

  loadSections(): void {
    this.isLoading = true;
    this.api.getSections(this.paperId).subscribe({
      next: (sections) => {
        this.sections = sections;
        this.isLoading = false;
      },
      error: () => {
        this.isLoading = false;
      },
    });
  }

  selectSection(title: string): void {
    this.activeSection = title;
    this.sectionSelected.emit(title);
  }

  toggleExpand(title: string): void {
    this.expandedSection = this.expandedSection === title ? '' : title;
  }

  truncateText(text: string, maxLen = 200): string {
    if (text.length <= maxLen) return text;
    return text.substring(0, maxLen) + '...';
  }
}
