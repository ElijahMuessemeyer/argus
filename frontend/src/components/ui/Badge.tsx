import { HTMLAttributes, forwardRef } from 'react';
import { clsx } from 'clsx';

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: 'default' | 'bullish' | 'bearish' | 'neutral';
}

export const Badge = forwardRef<HTMLSpanElement, BadgeProps>(
  ({ className, variant = 'default', ...props }, ref) => {
    return (
      <span
        ref={ref}
        className={clsx(
          'inline-flex items-center px-2 py-0.5 rounded text-xs font-medium',
          {
            'bg-gray-700 text-gray-300': variant === 'default',
            'bg-green-900/50 text-green-400': variant === 'bullish',
            'bg-red-900/50 text-red-400': variant === 'bearish',
            'bg-yellow-900/50 text-yellow-400': variant === 'neutral',
          },
          className
        )}
        {...props}
      />
    );
  }
);

Badge.displayName = 'Badge';
