import React from 'react';
import { SearchResult } from '@/lib/search-api';
import { Pill, Bell, FileText } from 'lucide-react';

interface SearchResultItemProps {
  result: SearchResult;
  isSelected: boolean;
  onSelect: (result: SearchResult) => void;
}

const getIcon = (type: SearchResult['type']) => {
  switch (type) {
    case 'medicine':
      return <Pill className="h-4 w-4 text-blue-500" />;
    case 'reminder':
      return <Bell className="h-4 w-4 text-green-500" />;
    case 'prescription':
      return <FileText className="h-4 w-4 text-purple-500" />;
  }
};

const getTypeLabel = (type: SearchResult['type']) => {
  switch (type) {
    case 'medicine':
      return 'Medicine';
    case 'reminder':
      return 'Reminder';
    case 'prescription':
      return 'Prescription';
  }
};

export default function SearchResultItem({
  result,
  isSelected,
  onSelect,
}: SearchResultItemProps) {
  return (
    <button
      className={`w-full flex items-center gap-3 px-3 py-2 text-left rounded-md transition-colors ${
        isSelected
          ? 'bg-primary text-primary-foreground'
          : 'hover:bg-secondary'
      }`}
      onClick={() => onSelect(result)}
    >
      {getIcon(result.type)}
      <div className="flex-1 min-w-0">
        <p className={`font-medium truncate ${isSelected ? 'text-primary-foreground' : ''}`}>
          {result.title}
        </p>
        <p className={`text-sm truncate ${isSelected ? 'text-primary-foreground/70' : 'text-muted-foreground'}`}>
          {result.subtitle}
        </p>
      </div>
      <span className={`text-xs px-2 py-0.5 rounded-full ${
        isSelected ? 'bg-primary-foreground/20 text-primary-foreground' : 'bg-secondary text-muted-foreground'
      }`}>
        {getTypeLabel(result.type)}
      </span>
    </button>
  );
}
