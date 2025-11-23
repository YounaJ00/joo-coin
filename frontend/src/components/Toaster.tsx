import { useToast } from '@/contexts/ToastContext';
import { X } from 'lucide-react';
import { useState } from 'react';

export function Toaster() {
  const { toasts } = useToast();
  const [dismissed, setDismissed] = useState<Set<string>>(new Set());

  const handleDismiss = (id: string) => {
    setDismissed((prev) => new Set(prev).add(id));
  };

  return (
    <div className="fixed top-4 right-4 z-50 flex flex-col gap-2">
      {toasts
        .filter((toast) => !dismissed.has(toast.id))
        .map((toast) => (
          <div
            key={toast.id}
            className={`rounded-lg border p-4 shadow-lg min-w-[300px] ${
              toast.variant === 'destructive'
                ? 'bg-destructive text-destructive-foreground'
                : 'bg-background text-foreground'
            }`}
          >
            <div className="flex items-start gap-2">
              <div className="flex-1">
                <div className="font-semibold">{toast.title}</div>
                {toast.description && (
                  <div className="text-sm opacity-90 mt-1">
                    {toast.description}
                  </div>
                )}
              </div>
              <button
                onClick={() => handleDismiss(toast.id)}
                className="hover:opacity-70 transition-opacity"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          </div>
        ))}
    </div>
  );
}

