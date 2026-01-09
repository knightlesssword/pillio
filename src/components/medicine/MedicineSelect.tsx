import React, { useState, useEffect, useRef } from 'react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Loader2, Search } from 'lucide-react';
import medicinesApi, { type MedicineDropdownItem } from '@/lib/medicines-api';

interface MedicineSelectProps {
  value: string;
  onChange: (value: string, medicine?: MedicineDropdownItem) => void;
  placeholder?: string;
  className?: string;
}

export function MedicineSelect({
  value,
  onChange,
  placeholder = "Search medicines...",
  className,
}: MedicineSelectProps) {
  const [search, setSearch] = useState(value);
  const [results, setResults] = useState<MedicineDropdownItem[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const wrapperRef = useRef<HTMLDivElement>(null);
  const isUserTypingRef = useRef(false);

  // Update search when value changes externally (e.g., from parent edit mode)
  // Mark as NOT user-typed so the search effect won't auto-open the dropdown
  // useEffect(() => {
  //   if (value && isNaN(Number(value))) {
  //     isUserTypingRef.current = false;
  //     setSearch(value);
  //   }
  // }, [value]);
  // This useeffect is commented as it was causing UI issues
  // Now the component is truly Uncontrolled.

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Search medicines when typing (debounced)
  useEffect(() => {
    const timer = setTimeout(async () => {
      if (search.length >= 2) {
        setIsLoading(true);
        try {
          const res = await medicinesApi.getForPrescription(search);
          setResults(res.data);
          if (res.data.length > 0 && isUserTypingRef.current) {
            setIsOpen(true);
          }
        } finally {
          setIsLoading(false);
        }
      } else {
        setResults([]);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [search]);

  const handleSelect = (medicine: MedicineDropdownItem) => {
    onChange(String(medicine.id), medicine);
    setSearch(`${medicine.name} - ${medicine.dosage}`);
    isUserTypingRef.current = false;
    setIsOpen(false);
  };

  const handleClear = () => {
    setSearch('');
    setResults([]);
    setIsOpen(false);
    onChange('');
  };

  return (
    <div ref={wrapperRef} className={`relative ${className}`}>
      <div className="flex gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            value={search}
            onChange={(e) => {
              isUserTypingRef.current = true;
              setSearch(e.target.value);
              onChange(e.target.value);
            }}
            placeholder={placeholder}
            onFocus={() => {
              isUserTypingRef.current = true;
              if (search.length >= 2) {
                setIsOpen(true);
              }
            }}
            className="pl-10"
          />
          {isLoading && (
            <Loader2 className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 animate-spin text-muted-foreground" />
          )}
        </div>
        {value && (
          <Button type="button" variant="outline" onClick={handleClear}>
            Clear
          </Button>
        )}
      </div>

      {isOpen && search.length >= 2 && (
        <div className="absolute z-10 w-full border rounded-md bg-popover mt-1 max-h-60 overflow-auto shadow-lg">
          {results.length > 0 ? (
            results.map((med) => (
              <div
                key={med.id}
                className="px-4 py-3 hover:bg-accent cursor-pointer border-b last:border-b-0"
                onClick={() => handleSelect(med)}
              >
                <div className="font-medium">{med.name}</div>
                <div className="text-sm text-muted-foreground flex gap-2">
                  <span>{med.dosage}</span>
                  <span>•</span>
                  <span>{med.form}</span>
                  <span>•</span>
                  <span>{med.unit}</span>
                </div>
              </div>
            ))
          ) : (
            <div className="p-4 text-center text-muted-foreground">
              No medicines found. Enter manually below.
            </div>
          )}
        </div>
      )}
    </div>
  );
}
