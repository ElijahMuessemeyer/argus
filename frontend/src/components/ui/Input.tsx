import { InputHTMLAttributes, forwardRef } from 'react';
import { clsx } from 'clsx';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  error?: boolean;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, error, ...props }, ref) => {
    return (
      <input
        ref={ref}
        className={clsx(
          'w-full bg-gray-800 border rounded-lg px-3 py-2 text-gray-100',
          'placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500',
          'focus:border-transparent transition-colors',
          error ? 'border-red-500' : 'border-gray-600',
          className
        )}
        {...props}
      />
    );
  }
);

Input.displayName = 'Input';
