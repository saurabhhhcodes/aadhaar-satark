import React from 'react';
import { X, AlertTriangle, CheckCircle, Clock, TrendingUp, Users, Activity, FileText, Download } from 'lucide-react';
import { DistrictData, downloadReport } from '@/services/api';

interface ReportModalProps {
    isOpen: boolean;
    onClose: () => void;
    district: DistrictData | null;
}

export function ReportModal({ isOpen, onClose, district }: ReportModalProps) {
    if (!isOpen || !district) return null;

    // --- AI Narrative Generation Logic ---
    const generateNarrative = (d: DistrictData) => {
        const isCritical = d.status === 'CRITICAL';
        const isModerate = d.status === 'MODERATE';

        let summary = "";
        let actionPlan = [];
        let riskLevel = "";

        if (isCritical) {
            riskLevel = "High Probability of Service Disruption";
            summary = `${d.district} is identified as a critical priority zone. With a ${d.gap_percentage}% deficit in mandatory biometric updates, a significant portion of the 5-17 age demographic is at risk of non-compliance. This pattern strongly suggests a bottleneck in local enrolment infrastructure or a substantial demographic shift that has not been accounted for.`;
            actionPlan = [
                "Immediate Deployment: Dispatch mobile enrolment units to high-density school zones.",
                "Camp Scheduling: Organize weekend mandate-update camps within a 5km radius of deficit hotspots.",
                "Targeted Notification: Trigger SMS alerts to residents with pending updates to drive footfall."
            ];
        } else if (isModerate) {
            riskLevel = "Moderate Risk of Backlog Accumulation";
            summary = `${d.district} is showing early signs of update lag (${d.gap_percentage}%). While not yet critical, the trend suggests that without intervention, the backlog could grow by 15-20% in the next quarter. Proactive measures are recommended to stabilize the metric before it reaches a critical threshold.`;
            actionPlan = [
                "Capacity Planning: Temporarily increase operator shifts in existing Permanent Enrolment Centers (PEKs).",
                "School Outreach: Coordinate with local school boards for on-site update drives.",
                "Monitoring: Initiate weekly reviews of daily packet upload counts to track improvement."
            ];
        } else {
            riskLevel = "Low Risk - Operational Stability";
            summary = `${d.district} is performing optimally. The ${d.gap_percentage}% gap is well within the acceptable operational threshold. The existing infrastructure is successfully meeting the daily update demand for the 5-17 age bracket. No immediate corrective action is required.`;
            actionPlan = [
                "Maintenance: Continue standard operational procedures and regular equipment maintenance.",
                "Optimization: Consider reallocating any excess resources to neighboring critical districts if available.",
                "Review: Conduct monthly performance audits to ensure sustained compliance."
            ];
        }

        return { summary, actionPlan, riskLevel };
    };

    const { summary, actionPlan, riskLevel } = generateNarrative(district);

    const handleDownload = () => {
        downloadReport(district);
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-in fade-in duration-200">
            <div
                className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col animate-in zoom-in-95 duration-200 border border-slate-200"
                onClick={(e) => e.stopPropagation()}
            >
                {/* Header */}
                <div className="bg-slate-50 px-6 py-4 border-b border-slate-200 flex justify-between items-center">
                    <div className="flex items-center gap-3">
                        <div className={`p-2 rounded-lg ${district.status === 'CRITICAL' ? 'bg-red-100 text-red-600' : district.status === 'MODERATE' ? 'bg-yellow-100 text-yellow-600' : 'bg-emerald-100 text-emerald-600'}`}>
                            <FileText className="w-5 h-5" />
                        </div>
                        <div>
                            <h2 className="text-xl font-bold text-slate-800">Strategic Analysis Report</h2>
                            <p className="text-sm text-slate-500">{district.district}, {district.state}</p>
                        </div>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-2 hover:bg-slate-200 rounded-full text-slate-500 transition-colors"
                    >
                        <X className="w-5 h-5" />
                    </button>
                </div>

                {/* Scrollable Content */}
                <div className="p-6 overflow-y-auto custom-scrollbar space-y-8">

                    {/* Status Banner */}
                    <div className={`flex items-start gap-4 p-4 rounded-xl border ${district.status === 'CRITICAL' ? 'bg-red-50 border-red-100' :
                            district.status === 'MODERATE' ? 'bg-amber-50 border-amber-100' :
                                'bg-emerald-50 border-emerald-100'
                        }`}>
                        {district.status === 'CRITICAL' ? <AlertTriangle className="w-6 h-6 text-red-600 shrink-0" /> :
                            district.status === 'MODERATE' ? <Clock className="w-6 h-6 text-amber-600 shrink-0" /> :
                                <CheckCircle className="w-6 h-6 text-emerald-600 shrink-0" />
                        }
                        <div>
                            <h3 className={`font-bold ${district.status === 'CRITICAL' ? 'text-red-900' :
                                    district.status === 'MODERATE' ? 'text-amber-900' :
                                        'text-emerald-900'
                                }`}>
                                AI Assessment: {district.status}
                            </h3>
                            <p className={`text-sm mt-1 ${district.status === 'CRITICAL' ? 'text-red-700' :
                                    district.status === 'MODERATE' ? 'text-amber-700' :
                                        'text-emerald-700'
                                }`}>
                                {riskLevel}
                            </p>
                        </div>
                    </div>

                    {/* Executive Summary */}
                    <section>
                        <h4 className="flex items-center gap-2 text-sm font-semibold uppercase tracking-wider text-slate-500 mb-3">
                            <Activity className="w-4 h-4" /> Executive Summary
                        </h4>
                        <p className="text-slate-700 leading-relaxed text-base border-l-4 border-indigo-500 pl-4">
                            {summary}
                        </p>
                    </section>

                    {/* Key Metrics Grid */}
                    <section>
                        <h4 className="flex items-center gap-2 text-sm font-semibold uppercase tracking-wider text-slate-500 mb-3">
                            <TrendingUp className="w-4 h-4" /> Key Performance Indicators
                        </h4>
                        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                            <div className="bg-slate-50 p-4 rounded-lg border border-slate-100">
                                <p className="text-xs text-slate-500 mb-1">Target Updates</p>
                                <p className="text-xl font-bold text-slate-800">{district.expected_updates.toLocaleString()}</p>
                            </div>
                            <div className="bg-slate-50 p-4 rounded-lg border border-slate-100">
                                <p className="text-xs text-slate-500 mb-1">Completed</p>
                                <p className="text-xl font-bold text-slate-800">{district.actual_updates.toLocaleString()}</p>
                            </div>
                            <div className="bg-slate-50 p-4 rounded-lg border border-slate-100 relative overflow-hidden">
                                <div className={`absolute top-0 right-0 w-16 h-16 rounded-bl-full opacity-10 ${district.status === 'CRITICAL' ? 'bg-red-500' : 'bg-emerald-500'
                                    }`} />
                                <p className="text-xs text-slate-500 mb-1">Pending Gap</p>
                                <p className={`text-xl font-bold ${district.status === 'CRITICAL' ? 'text-red-600' : 'text-slate-800'}`}>
                                    {district.pending_updates.toLocaleString()}
                                </p>
                            </div>
                        </div>
                    </section>

                    {/* Recommended Action Plan */}
                    <section>
                        <h4 className="flex items-center gap-2 text-sm font-semibold uppercase tracking-wider text-slate-500 mb-3">
                            <Users className="w-4 h-4" /> Recommended Action Plan
                        </h4>
                        <div className="bg-indigo-50/50 rounded-xl p-5 border border-indigo-100">
                            <ul className="space-y-3">
                                {actionPlan.map((action, i) => (
                                    <li key={i} className="flex gap-3 text-slate-700">
                                        <div className="w-6 h-6 rounded-full bg-indigo-100 text-indigo-600 flex items-center justify-center text-xs font-bold shrink-0 mt-0.5">
                                            {i + 1}
                                        </div>
                                        <span className="text-sm">{action}</span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    </section>
                </div>

                {/* Footer */}
                <div className="bg-slate-50 px-6 py-4 border-t border-slate-200 flex justify-end gap-3">
                    <button
                        onClick={onClose}
                        className="px-4 py-2 text-sm font-medium text-slate-600 hover:text-slate-800 transition-colors"
                    >
                        Close Analysis
                    </button>
                    <button
                        onClick={handleDownload}
                        className="px-4 py-2 text-sm font-medium bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 shadow-sm transition-colors flex items-center gap-2"
                    >
                        <Download className="w-4 h-4" /> Export PDF
                    </button>
                </div>
            </div>
        </div>
    );
}
