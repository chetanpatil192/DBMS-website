import React from 'react';

interface CardProps {
  title?: string;
  subtitle?: string;
  badge?: React.ReactNode;
  children: React.ReactNode;
  footer?: React.ReactNode;
  className?: string;
}

export const Card: React.FC<CardProps> = ({
  title,
  subtitle,
  badge,
  children,
  footer,
  className = '',
}) => {
  return (
    <div className={`rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden ${className}`}>
      {(title || subtitle || badge) && (
        <div className="border-b border-slate-100 px-6 py-4 flex items-center justify-between">
          <div>
            {title && <h3 className="text-base font-semibold text-slate-900">{title}</h3>}
            {subtitle && <p className="text-xs text-slate-500 mt-0.5">{subtitle}</p>}
          </div>
          {badge && <div>{badge}</div>}
        </div>
      )}
      <div className="p-6">{children}</div>
      {footer && <div className="border-t border-slate-100 bg-slate-50/50 px-6 py-3">{footer}</div>}
    </div>
  );
};
