import React from 'react';
import { SearchResult, SearchResultType } from '@/lib/search-api';
import SearchResultItem from './SearchResultItem';

interface SearchResultGroupProps {
  type: SearchResultType;
  results: SearchResult[];
  selectedIndex: number;
  onSelect: (result: SearchResult) => void;
}

const getTypeLabel = (type: SearchResultType): string => {
  switch (type) {
    case 'medicine':
      return 'Medicines';
    case 'reminder':
      return 'Reminders';
    case 'prescription':
      return 'Prescriptions';
  }
};

interface GroupedResults {
  [key: string]: SearchResult[];
}

export default function SearchResultGroup({
  type,
  results,
  selectedIndex,
  onSelect,
}: SearchResultGroupProps) {
  if (results.length === 0) return null;

  const startIndex = getStartIndex(type);
  const endIndex = startIndex + results.length;

  return (
    <div className="mb-2">
      <p className="px-3 py-1.5 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
        {getTypeLabel(type)}
      </p>
      <div className="space-y-0.5">
        {results.map((result, index) => (
          <SearchResultItem
            key={result.id}
            result={result}
            isSelected={selectedIndex >= startIndex && selectedIndex < endIndex && index === selectedIndex - startIndex}
            onSelect={onSelect}
          />
        ))}
      </div>
    </div>
  );
}

function getStartIndex(type: SearchResultType): number {
  switch (type) {
    case 'medicine':
      return 0;
    case 'reminder':
      return 0; // Will be recalculated based on actual counts
    case 'prescription':
      return 0;
  }
}
