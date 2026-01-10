import React, { useState } from 'react';
import { Trash2, Loader2, AlertTriangle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { authApi } from '@/lib/auth-api';
import { useAuth } from '@/contexts/AuthContext';
import { useToast } from '@/hooks/use-toast';

export function DeleteAccountDialog() {
  const [open, setOpen] = useState(false);
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { logout } = useAuth();
  const { toast } = useToast();

  const handleDelete = async () => {
    if (!password) {
      toast({
        title: 'Password Required',
        description: 'Please enter your password to verify.',
        variant: 'destructive',
      });
      return;
    }

    setIsLoading(true);
    try {
      await authApi.deleteAccount({ password, reason: 'User requested account deletion' });

      toast({
        title: 'Account Deleted',
        description: 'Your account has been deleted. You have 14 days to restore it by logging in again.',
      });

      // Clear local storage and logout
      localStorage.removeItem('auth_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
      setOpen(false);
      logout();
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to delete account';
      toast({
        title: 'Deletion Failed',
        description: errorMessage,
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="destructive">
          <Trash2 className="mr-2 h-4 w-4" />
          Delete Account
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-destructive">
            <AlertTriangle className="h-5 w-5" />
            Delete Account
          </DialogTitle>
          <DialogDescription>
            This action cannot be undone. This will permanently delete your account and all associated data.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          <div className="rounded-lg bg-destructive/10 p-4 text-sm text-destructive">
            <p className="font-medium mb-2">What happens when you delete your account:</p>
            <ul className="list-disc list-inside space-y-1">
              <li>Your account will be deactivated immediately.</li>
              <li>You have 14 days to restore by logging in again.</li>
              <li>After 14 days, your data will be permanently deleted.</li>
              <li>Consider exporting your data before deleting.</li>
            </ul>
          </div>

          <div className="space-y-2">
            <Label htmlFor="password">Enter your password to confirm</Label>
            <Input
              id="password"
              type="password"
              placeholder="Your current password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={isLoading}
            />
          </div>
        </div>

        <DialogFooter className="sm:justify-between">
          <Button
            variant="outline"
            onClick={() => setOpen(false)}
            disabled={isLoading}
          >
            Cancel
          </Button>
          <Button
            variant="destructive"
            onClick={handleDelete}
            disabled={isLoading || !password}
          >
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Deleting...
              </>
            ) : (
              <>
                <Trash2 className="mr-2 h-4 w-4" />
                Delete Account
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

export default DeleteAccountDialog;
