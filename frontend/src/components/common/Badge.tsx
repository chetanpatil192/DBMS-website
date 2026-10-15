import React from 'react';

export type BadgeVariant = 'success' | 'warning' | 'danger' | 'info' | 'neutral';

interface BadgeProps {
  children: React.ReactNode;
  variant?: BadgeVariant;
  size?: 'sm' | 'md';
  dot?: boolean;
}

const variantStyles: Record<BadgeVariant, { bg: string; text: string; dotColor: string; border: string }> = {
  success: {
    bg: 'bg-emerald-50',
    text: 'text-emerald-700',
    dotColor: 'bg-emerald-500',
    border: 'border-emerald-200',
  },
  warning: {
    bg: 'bg-amber-50',
    text: 'text-amber-700',
    dotColor: 'bg-amber-500',
    border: 'border-amber-200',
  },
  danger: {
    bg: 'bg-rose-50',
    text: 'text-rose-700',
    dotColor: 'bg-rose-500',
    border: 'border-rose-200',
  },
  info: {
    bg: 'bg-sky-50',
    text: 'text-sky-700',
    dotColor: 'bg-sky-500',
    border: 'border-sky-200',
  },
  neutral: {
    bg: 'bg-slate-100',
    text: 'text-slate-700',
    dotColor: 'bg-slate-400',
    border: 'border-slate-200',
  },
};

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'neutral',
  size = 'md',
  dot = false,
}) => {
  const styles = variantStyles[variant];
  const sizeClasses = size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-2.5 py-1 text-xs font-medium';

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border ${styles.bg} ${styles.text} ${styles.border} ${sizeClasses}`}
    >
      {dot && <span className={`h-1.5 w-1.5 rounded-full ${styles.dotColor}`} />}
      {children}
    </span>
  );
};
