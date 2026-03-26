import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { UploadComponent } from './components/upload/upload.component';
import { ChatComponent } from './components/chat/chat.component';
import { SectionsComponent } from './components/sections/sections.component';
import { SummaryComponent } from './components/summary/summary.component';
import { UploadResponse } from './services/api.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, UploadComponent, ChatComponent, SectionsComponent, SummaryComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css',
})
export class AppComponent {
  currentView: 'upload' | 'analyze' = 'upload';
  paperId = '';
  paperTitle = '';
  paperAuthors: string[] = [];
  totalPages = 0;
  numChunks = 0;
  activeTab: 'chat' | 'summary' = 'chat';

  onPaperUploaded(response: UploadResponse): void {
    this.paperId = response.paper_id;
    this.paperTitle = response.metadata.title;
    this.paperAuthors = response.metadata.authors;
    this.totalPages = response.metadata.total_pages;
    this.numChunks = response.num_chunks;
    this.currentView = 'analyze';
  }

  uploadNew(): void {
    this.currentView = 'upload';
    this.paperId = '';
    this.paperTitle = '';
    this.paperAuthors = [];
    this.activeTab = 'chat';
  }

  switchTab(tab: 'chat' | 'summary'): void {
    this.activeTab = tab;
  }

  isDarkMode = true;

  toggleTheme(): void {
    this.isDarkMode = !this.isDarkMode;
    if (this.isDarkMode) {
      document.documentElement.removeAttribute('data-theme');
    } else {
      document.documentElement.setAttribute('data-theme', 'light');
    }
  }
}
