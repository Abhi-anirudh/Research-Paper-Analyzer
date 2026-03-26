import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface PaperMetadata {
  paper_id: string;
  title: string;
  authors: string[];
  abstract: string;
  sections: string[];
  total_pages: number;
  filename: string;
}

export interface UploadResponse {
  paper_id: string;
  metadata: PaperMetadata;
  num_chunks: number;
  message: string;
}

export interface SourceChunk {
  text: string;
  section_title: string;
  page_number: number;
  similarity_score: number;
}

export interface QueryResponse {
  answer: string;
  sources: SourceChunk[];
  grounded: boolean;
}

export interface Section {
  title: string;
  text: string;
  page_numbers: number[];
}

export interface SummaryResponse {
  paper_id: string;
  level: string;
  summary: string;
  sections: Section[];
}

export interface CompareResponse {
  answer: string;
  sources: { [key: string]: SourceChunk[] };
}

@Injectable({ providedIn: 'root' })
export class ApiService {
  // Use relative /api path when deployed (proxied via nginx), and localhost:8000 for local development
  private baseUrl = window.location.hostname === 'localhost' ? 'http://localhost:8000/api' : '/api';

  constructor(private http: HttpClient) {}

  uploadPaper(file: File): Observable<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post<UploadResponse>(`${this.baseUrl}/upload-paper`, formData);
  }

  queryPaper(paperId: string, question: string, topK: number = 5): Observable<QueryResponse> {
    return this.http.post<QueryResponse>(`${this.baseUrl}/query`, {
      paper_id: paperId,
      question,
      top_k: topK,
    });
  }

  detectNovelty(paperId: string): Observable<QueryResponse> {
    return this.http.post<QueryResponse>(`${this.baseUrl}/query/novelty`, {
      paper_id: paperId,
      question: 'What makes this paper novel?',
    });
  }

  extractInsights(paperId: string): Observable<QueryResponse> {
    return this.http.post<QueryResponse>(`${this.baseUrl}/query/insights`, {
      paper_id: paperId,
      question: 'What are the key insights?',
    });
  }

  getSummary(paperId: string, level: 'beginner' | 'technical'): Observable<SummaryResponse> {
    const params = new HttpParams().set('level', level);
    return this.http.get<SummaryResponse>(`${this.baseUrl}/summary/${paperId}`, { params });
  }

  getSections(paperId: string): Observable<Section[]> {
    return this.http.get<Section[]>(`${this.baseUrl}/summary/${paperId}/sections`);
  }

  comparePapers(paperIds: string[], question: string): Observable<CompareResponse> {
    return this.http.post<CompareResponse>(`${this.baseUrl}/compare`, {
      paper_ids: paperIds,
      question,
    });
  }

  generateLiteratureReview(paperIds: string[]): Observable<CompareResponse> {
    return this.http.post<CompareResponse>(`${this.baseUrl}/literature-review`, {
      paper_ids: paperIds,
      question: 'Generate literature review',
    });
  }
}
