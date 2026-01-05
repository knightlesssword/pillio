import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"
import { format, formatDistanceToNow, isToday, isTomorrow, isYesterday, parseISO } from "date-fns"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// Format date for display
export function formatDate(date: Date | string, formatString: string = 'PPP'): string {
  const parsedDate = typeof date === 'string' ? parseISO(date) : date;
  return format(parsedDate, formatString);
}

// Format time for display
export function formatTime(date: Date | string): string {
  const parsedDate = typeof date === 'string' ? parseISO(date) : date;
  return format(parsedDate, 'h:mm a');
}

// Get relative date string
export function getRelativeDate(date: Date | string): string {
  const parsedDate = typeof date === 'string' ? parseISO(date) : date;
  
  if (isToday(parsedDate)) return 'Today';
  if (isTomorrow(parsedDate)) return 'Tomorrow';
  if (isYesterday(parsedDate)) return 'Yesterday';
  
  return formatDistanceToNow(parsedDate, { addSuffix: true });
}

// Calculate stock level status
export function getStockStatus(current: number, minimum: number): 'critical' | 'low' | 'medium' | 'good' {
  const percentage = (current / minimum) * 100;
  
  if (percentage <= 25) return 'critical';
  if (percentage <= 50) return 'low';
  if (percentage <= 75) return 'medium';
  return 'good';
}

// Get stock status color
export function getStockStatusColor(status: 'critical' | 'low' | 'medium' | 'good'): string {
  switch (status) {
    case 'critical': return 'bg-destructive text-destructive-foreground';
    case 'low': return 'bg-warning text-warning-foreground';
    case 'medium': return 'bg-info text-info-foreground';
    case 'good': return 'bg-success text-success-foreground';
  }
}

// Calculate adherence percentage
export function calculateAdherence(taken: number, total: number): number {
  if (total === 0) return 100;
  return Math.round((taken / total) * 100);
}

// Generate unique ID
export function generateId(): string {
  return Math.random().toString(36).substring(2, 9);
}

// Capitalize first letter
export function capitalize(str: string): string {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

// Truncate text
export function truncate(str: string, length: number): string {
  if (str.length <= length) return str;
  return str.slice(0, length) + '...';
}

// Format number with suffix
export function formatNumber(num: number): string {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
  return num.toString();
}

// Get greeting based on time of day
export function getGreeting(): string {
  const hour = new Date().getHours();
  
  if (hour < 12) return 'Good morning';
  if (hour < 17) return 'Good afternoon';
  if (hour < 21) return 'Good evening';
  return 'Good night';
}

// Validate email
export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

// Format phone number
export function formatPhoneNumber(phone: string): string {
  const cleaned = phone.replace(/\D/g, '');
  const match = cleaned.match(/^(\d{3})(\d{3})(\d{4})$/);
  if (match) {
    return '(' + match[1] + ') ' + match[2] + '-' + match[3];
  }
  return phone;
}

// Debounce function
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout;
  
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}

// Sleep function for async operations
export function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Get initials from name
export function getInitials(name: string): string {
  return name
    .split(' ')
    .map(part => part[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);
}

// Parse time string to date
export function parseTimeString(timeString: string): Date {
  const [hours, minutes] = timeString.split(':').map(Number);
  const date = new Date();
  date.setHours(hours, minutes, 0, 0);
  return date;
}

// Get days until date
export function getDaysUntil(date: Date | string): number {
  const parsedDate = typeof date === 'string' ? parseISO(date) : date;
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const targetDate = new Date(parsedDate);
  targetDate.setHours(0, 0, 0, 0);
  
  const diffTime = targetDate.getTime() - today.getTime();
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
}
