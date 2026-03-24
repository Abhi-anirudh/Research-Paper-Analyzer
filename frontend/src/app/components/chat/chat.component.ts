import { Component, Input, ViewChild, ElementRef, AfterViewChecked } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService, QueryResponse, SourceChunk } from '../../services/api.service';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  sources?: SourceChunk[];
  grounded?: boolean;
  timestamp: Date;
  isLoading?: boolean;
}

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './chat.component.html',
  styleUrl: './chat.component.css',
})
export class ChatComponent implements AfterViewChecked {
  @Input() paperId = '';
  @Input() paperTitle = '';
  @ViewChild('messagesContainer') private messagesContainer!: ElementRef;

  messages: ChatMessage[] = [];
  currentQuestion = '';
  isLoading = false;
  expandedSources: Set<number> = new Set();

  quickQuestions = [
    'Explain this paper simply',
    'What is the main contribution?',
    'What are the limitations?',
    'What makes this paper different?',
    'What are the key findings?',
  ];

  constructor(private api: ApiService) {}

  ngAfterViewChecked(): void {
    this.scrollToBottom();
  }

  sendMessage(question?: string): void {
    const q = question || this.currentQuestion.trim();
    if (!q || this.isLoading || !this.paperId) return;

    this.messages.push({
      role: 'user',
      content: q,
      timestamp: new Date(),
    });

    this.messages.push({
      role: 'assistant',
      content: '',
      timestamp: new Date(),
      isLoading: true,
    });

    this.currentQuestion = '';
    this.isLoading = true;

    this.api.queryPaper(this.paperId, q).subscribe({
      next: (response: QueryResponse) => {
        this.messages[this.messages.length - 1] = {
          role: 'assistant',
          content: response.answer,
          sources: response.sources,
          grounded: response.grounded,
          timestamp: new Date(),
          isLoading: false,
        };
        this.isLoading = false;
      },
      error: (err) => {
        this.messages[this.messages.length - 1] = {
          role: 'assistant',
          content: 'Sorry, an error occurred while processing your question. Please try again.',
          timestamp: new Date(),
          isLoading: false,
          grounded: false,
        };
        this.isLoading = false;
      },
    });
  }

  toggleSources(index: number): void {
    if (this.expandedSources.has(index)) {
      this.expandedSources.delete(index);
    } else {
      this.expandedSources.add(index);
    }
  }

  isSourceExpanded(index: number): boolean {
    return this.expandedSources.has(index);
  }

  onKeyDown(event: KeyboardEvent): void {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.sendMessage();
    }
  }

  private scrollToBottom(): void {
    try {
      const el = this.messagesContainer?.nativeElement;
      if (el) el.scrollTop = el.scrollHeight;
    } catch {}
  }
}
