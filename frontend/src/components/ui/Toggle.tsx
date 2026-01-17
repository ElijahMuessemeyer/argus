import { clsx } from 'clsx';

interface ToggleProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
  label?: string;
  size?: 'sm' | 'md';
}

export function Toggle({ checked, onChange, label, size = 'md' }: ToggleProps) {
  return (
    <label className="inline-flex items-center cursor-pointer">
      <button
        type="button"
        role="switch"
        aria-checked={checked}
        onClick={() => onChange(!checked)}
        className={clsx(
          'relative inline-flex shrink-0 rounded-full transition-colors',
          'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-gray-900',
          checked ? 'bg-blue-600' : 'bg-gray-600',
          {
            'h-5 w-9': size === 'sm',
            'h-6 w-11': size === 'md',
          }
        )}
      >
        <span
          className={clsx(
            'inline-block rounded-full bg-white transition-transform',
            {
              'h-4 w-4 translate-x-0.5': size === 'sm',
              'h-5 w-5 translate-x-0.5': size === 'md',
            },
            checked && {
              'translate-x-4': size === 'sm',
              'translate-x-5': size === 'md',
            },
            'mt-0.5'
          )}
        />
      </button>
      {label && (
        <span className="ml-2 text-sm text-gray-300">{label}</span>
      )}
    </label>
  );
}
