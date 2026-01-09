import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Loader2, X } from 'lucide-react';
import { searchApi, SearchResult, SearchResultType } from '@/lib/search-api';
import { useDebounce } from '@/hooks/use-debounce';
import SearchResultGroup from './SearchResultGroup';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

const MIN_QUERY_LENGTH = 2;
const MAX_RESULTS_PER_TYPE = 5;

export default function UniversalSearch() {
  const navigate = useNavigate();
  const [query, setQuery] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const [results, setResults] = useState<SearchResult[]>([]);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  
  const debouncedQuery = useDebounce(query, 300);
  const inputRef = useRef<HTMLInputElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Search when debounced query changes
  useEffect(() => {
    if (debouncedQuery.length >= MIN_QUERY_LENGTH) {
      performSearch(debouncedQuery);
    } else {
      setResults([]);
      setHasSearched(false);
    }
  }, [debouncedQuery]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const performSearch = async (searchQuery: string) => {
    setIsLoading(true);
    try {
      const response = await searchApi.search(searchQuery);
      setResults(response.data.results.slice(0, MAX_RESULTS_PER_TYPE * 3));
      setHasSearched(true);
      setSelectedIndex(0);
    } catch (error) {
      console.error('Search failed:', error);
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelect = useCallback((result: SearchResult) => {
    navigate(result.route);
    setIsOpen(false);
    setQuery('');
  }, [navigate]);

  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    const totalResults = results.length;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedIndex(prev => (prev + 1) % totalResults);
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex(prev => (prev - 1 + totalResults) % totalResults);
        break;
      case 'Enter':
        e.preventDefault();
        if (totalResults > 0 && results[selectedIndex]) {
          handleSelect(results[selectedIndex]);
        }
        break;
      case 'Escape':
        e.preventDefault();
        setIsOpen(false);
        inputRef.current?.blur();
        break;
    }
  }, [results, selectedIndex, handleSelect]);

  const handleFocus = () => {
    setIsOpen(true);
    if (query.length >= MIN_QUERY_LENGTH && results.length > 0) {
      setIsOpen(true);
    }
  };

  const handleClear = () => {
    setQuery('');
    setResults([]);
    setHasSearched(false);
    inputRef.current?.focus();
  };

  const groupedResults = results.reduce((acc, result) => {
    if (!acc[result.type]) {
      acc[result.type] = [];
    }
    acc[result.type].push(result);
    return acc;
  }, {} as Record<SearchResultType, SearchResult[]>);

  const totalCount = results.length;

  return (
    <div className="relative w-full" ref={containerRef}>
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          ref={inputRef}
          type="search"
          placeholder="Search medicines, reminders..."
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setIsOpen(true);
          }}
          onFocus={handleFocus}
          onKeyDown={handleKeyDown}
          className="pl-10 pr-10 bg-secondary/50 border-0 focus:bg-card"
        />
        {query && (
          <Button
            variant="ghost"
            size="icon"
            className="absolute right-1 top-1/2 -translate-y-1/2 h-7 w-7"
            onClick={handleClear}
          >
            <X className="h-4 w-4" />
          </Button>
        )}
      </div>

      {isOpen && query.length >= MIN_QUERY_LENGTH && (
        <div className="absolute top-full left-0 right-0 mt-2 bg-card border rounded-lg shadow-lg max-h-96 overflow-y-auto z-50">
          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
            </div>
          ) : hasSearched ? (
            totalCount > 0 ? (
              <div className="py-2">
                {(['medicine', 'reminder', 'prescription'] as SearchResultType[]).map(type => (
                  groupedResults[type] && (
                    <SearchResultGroup
                      key={type}
                      type={type}
                      results={groupedResults[type]}
                      selectedIndex={selectedIndex}
                      onSelect={handleSelect}
                    />
                  )
                ))}
              </div>
            ) : (
              <div className="py-8 text-center text-muted-foreground">
                <p>No results found for "{query}"</p>
                <p className="text-sm mt-1">Try a different search term</p>
              </div>
            )
          ) : null}
        </div>
      )}
    </div>
  );
}
