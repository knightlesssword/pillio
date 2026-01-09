// Universal Search API service for FastAPI backend
import api from './api';
import type { AxiosResponse } from 'axios';

// Search result types
export type SearchResultType = 'medicine' | 'reminder' | 'prescription';

export interface SearchResult {
  id: string;
  type: SearchResultType;
  title: string;
  subtitle: string;
  route: string;
}

export interface SearchResponse {
  results: SearchResult[];
  total: number;
}

export const searchApi = {
  // Universal search across all entities
  search: (query: string): Promise<AxiosResponse<SearchResponse>> =>
    api.get<SearchResponse>('/search', { params: { q: query } }),
};

export default searchApi;
