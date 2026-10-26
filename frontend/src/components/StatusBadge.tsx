import React from 'react';
import { CheckCircle2, AlertTriangle, HelpCircle, ShieldAlert, AlertCircle, Info } from 'lucide-react';

interface StatusBadgeProps {
  status: string;
  size?: 'sm' | 'md';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, size = 'md' }) => {
  const norm = status.toLowerCase();

  const px = size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-2.5 py-1 text-sm';
  const iconSize = size === 'sm' ? 14 : 16;

  // Truth States
  if (norm === 'consistent') {
    return (
      <span className={`inline-flex items-center gap-1.5 font-medium rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 ${px}`}>
        <CheckCircle2 size={iconSize} className="text-emerald-600 shrink-0" />
        Consistent
      </span>
    );
  }

  if (norm.includes('potential') || norm.includes('inconsistency')) {
    return (
      <span className={`inline-flex items-center gap-1.5 font-medium rounded-full bg-amber-50 text-amber-800 border border-amber-200 ${px}`}>
        <AlertTriangle size={iconSize} className="text-amber-600 shrink-0" />
        Potential inconsistency
      </span>
    );
  }

  if (norm.includes('needs') || norm.includes('review') || norm === 'unverified') {
    return (
      <span className={`inline-flex items-center gap-1.5 font-medium rounded-full bg-blue-50 text-blue-700 border border-blue-200 ${px}`}>
        <HelpCircle size={iconSize} className="text-blue-600 shrink-0" />
        Needs human review
      </span>
    );
  }

  // Severities
  if (norm === 'high' || norm === 'critical') {
    return (
      <span className={`inline-flex items-center gap-1.5 font-medium rounded-full bg-rose-50 text-rose-700 border border-rose-200 ${px}`}>
        <ShieldAlert size={iconSize} className="text-rose-600 shrink-0" />
        {status.toUpperCase()}
      </span>
    );
  }

  if (norm === 'medium') {
    return (
      <span className={`inline-flex items-center gap-1.5 font-medium rounded-full bg-amber-50 text-amber-700 border border-amber-200 ${px}`}>
        <AlertCircle size={iconSize} className="text-amber-600 shrink-0" />
        MEDIUM
      </span>
    );
  }

  if (norm === 'low' || norm === 'info') {
    return (
      <span className={`inline-flex items-center gap-1.5 font-medium rounded-full bg-slate-100 text-slate-700 border border-slate-200 ${px}`}>
        <Info size={iconSize} className="text-slate-500 shrink-0" />
        {status.toUpperCase()}
      </span>
    );
  }

  // Review Decisions
  if (norm === 'confirmed') {
    return (
      <span className={`inline-flex items-center gap-1.5 font-medium rounded-full bg-rose-50 text-rose-700 border border-rose-200 ${px}`}>
        <CheckCircle2 size={iconSize} className="text-rose-600 shrink-0" />
        Confirmed Mismatch
      </span>
    );
  }

  if (norm === 'dismissed') {
    return (
      <span className={`inline-flex items-center gap-1.5 font-medium rounded-full bg-slate-100 text-slate-600 border border-slate-200 ${px}`}>
        Dismissed
      </span>
    );
  }

  return (
    <span className={`inline-flex items-center gap-1.5 font-medium rounded-full bg-slate-100 text-slate-700 border border-slate-200 ${px}`}>
      {status}
    </span>
  );
};
