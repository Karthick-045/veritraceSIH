import React from 'react';
import { AuditEvent } from '../api/client';
import { History, UserCheck, FileUp, Sparkles, AlertCircle, Edit3 } from 'lucide-react';

interface AuditTimelineProps {
  events: AuditEvent[];
}

export const AuditTimeline: React.FC<AuditTimelineProps> = ({ events }) => {
  if (!events || events.length === 0) {
    return (
      <div className="p-8 text-center bg-white rounded-xl border border-slate-200">
        <History size={36} className="mx-auto text-slate-300 mb-2" />
        <p className="text-sm font-semibold text-slate-700">No Audit Events Logged</p>
        <p className="text-xs text-slate-400 mt-1">Actions on this case will appear here in an append-only timeline.</p>
      </div>
    );
  }

  const getEventIcon = (type: string) => {
    switch (type) {
      case 'CASE_CREATED':
        return <UserCheck size={16} className="text-blue-600" />;
      case 'DOC_UPLOADED':
        return <FileUp size={16} className="text-emerald-600" />;
      case 'OCR_EXTRACTED':
        return <Sparkles size={16} className="text-purple-600" />;
      case 'ANALYSIS_EXECUTED':
        return <AlertCircle size={16} className="text-amber-600" />;
      case 'FINDING_REVIEWED':
        return <UserCheck size={16} className="text-rose-600" />;
      case 'FIELD_CORRECTED':
        return <Edit3 size={16} className="text-indigo-600" />;
      default:
        return <History size={16} className="text-slate-500" />;
    }
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
      <div className="flex items-center justify-between pb-4 mb-4 border-b border-slate-100">
        <div>
          <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <History size={18} className="text-blue-600" />
            Append-Only Audit Trail
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            Cryptographically sealed and immutable log of all automated actions and reviewer decisions.
          </p>
        </div>
        <span className="text-xs font-mono px-2.5 py-1 bg-slate-100 text-slate-700 rounded-full border border-slate-200">
          {events.length} Recorded Events
        </span>
      </div>

      <div className="relative pl-6 space-y-6 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-200">
        {events.map((evt) => (
          <div key={evt.id} className="relative group">
            {/* Dot / Icon */}
            <div className="absolute -left-6 top-0 w-5 h-5 rounded-full bg-white border-2 border-slate-300 flex items-center justify-center group-hover:border-blue-600 transition">
              {getEventIcon(evt.event_type)}
            </div>

            <div className="bg-slate-50 border border-slate-200/80 rounded-lg p-3.5 hover:bg-white hover:border-blue-200 hover:shadow-sm transition">
              <div className="flex items-center justify-between text-xs">
                <span className="font-mono font-bold text-slate-800 uppercase tracking-wider">
                  {evt.event_type}
                </span>
                <span className="text-slate-500 font-mono">
                  {new Date(evt.created_at).toLocaleString()}
                </span>
              </div>

              <div className="mt-2 text-xs text-slate-600 font-mono bg-white p-2.5 rounded border border-slate-200 overflow-x-auto">
                {JSON.stringify(evt.payload, null, 2)}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
