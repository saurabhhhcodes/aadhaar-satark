import React from 'react';
import { ProcessingResult } from '@/services/api';
import { StatCard } from './StatCard';
import { DistrictTable } from './DistrictTable';
import MapVisualizer from './MapVisualizer';
import { FileUpload } from './FileUpload';
import { ChatWidget } from './ChatWidget';
import { Users, AlertOctagon, TrendingUp, Activity, CheckCircle, RefreshCw, Globe } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface DashboardProps {
    data: ProcessingResult | null;
    onDataProcessed: (data: ProcessingResult) => void;
}

export function Dashboard({ data, onDataProcessed }: DashboardProps) {
    const [selectedState, setSelectedState] = React.useState<string>('All');
    const [isUploadOpen, setIsUploadOpen] = React.useState(false);
    const [isSyncing, setIsSyncing] = React.useState(false);
    const [syncStats, setSyncStats] = React.useState<any>(null);
    const [isMounted, setIsMounted] = React.useState(false);
    const [showToast, setShowToast] = React.useState(false);
    const hasSynced = React.useRef(false);

    React.useEffect(() => {
        setIsMounted(true);

        // Auto Sync Logic (Background)
        const performAutoSync = async () => {
            // Small delay to ensure initial render is smooth
            await new Promise(r => setTimeout(r, 1500));

            setIsSyncing(true);
            try {
                console.log("🔄 Auto-Syncing with Data.Gov.in...");
                const syncResponse = await fetch('http://localhost:8001/sync-official', { method: 'POST' });
                if (!syncResponse.ok) throw new Error("Sync API failed");
                const syncResult = await syncResponse.json();

                // Refresh Data
                const refreshResponse = await fetch('http://localhost:8001/initial-data');
                const newData = await refreshResponse.json();

                onDataProcessed(newData);

                // Show Success Toast
                setSyncStats({ newRecords: 0 }); // Placeholder if needed or just show status
                setShowToast(true);
                setTimeout(() => setShowToast(false), 5000);
            } catch (error) {
                console.warn("⚠️ Auto-Sync warning:", error);
                // Silent fail - don't disturb user
            } finally {
                setIsSyncing(false);
            }
        };
        if (!hasSynced.current) {
            hasSynced.current = true;
            performAutoSync();
        }
    }, []);

    if (!data || !data.districts || !Array.isArray(data.districts)) {
        // Fallback if data load failed or empty
        return (
            <div className="min-h-screen bg-slate-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
                <div className="text-center">
                    <h2 className="text-2xl font-bold text-slate-900">System Ready</h2>
                    <p className="mt-2 text-slate-600">No initial data found. Please upload manually or sync with official portal.</p>
                </div>
                <FileUpload onDataProcessed={onDataProcessed} />
            </div>
        );
    }

    // Extract unique states
    const states = ['All', ...Array.from(new Set(data.districts.map(d => d.state))).sort()];

    // Filtering State (Expanded to include Emerging/Compliant)
    const [statusFilter, setStatusFilter] = React.useState<'ALL' | 'CRITICAL' | 'MODERATE' | 'EMERGING' | 'COMPLIANT'>('ALL');

    // Filter Data
    const filteredDistricts = data.districts.filter(d => {
        const matchesState = selectedState === 'All' || d.state === selectedState;

        let matchesStatus = true;
        if (statusFilter === 'ALL') matchesStatus = true;
        else if (statusFilter === 'CRITICAL') matchesStatus = d.status === 'CRITICAL';
        else if (statusFilter === 'MODERATE') matchesStatus = d.status === 'MODERATE';
        else if (statusFilter === 'EMERGING') matchesStatus = d.status === 'SAFE' && d.gap_percentage > 0;
        else if (statusFilter === 'COMPLIANT') matchesStatus = d.status === 'SAFE' && d.gap_percentage === 0;

        return matchesState && matchesStatus;
    });

    // Prepare chart data (Top 10 critical districts in current view)
    const chartData = [...filteredDistricts]
        .sort((a, b) => b.gap_percentage - a.gap_percentage)
        .slice(0, 10);

    return (
        <div className="min-h-screen bg-slate-50 pb-12 relative">
            {/* Sync Modal */}
            {/* Auto Sync Toast Notification */}
            {showToast && (
                <div className="fixed bottom-6 left-6 z-50 animate-bounce-in">
                    <div className="bg-slate-900 border border-slate-700 text-white px-6 py-4 rounded-xl shadow-2xl flex items-center gap-4">
                        <div className="bg-emerald-500/20 p-2 rounded-full">
                            <RefreshCw className="w-5 h-5 text-emerald-400" />
                        </div>
                        <div>
                            <h4 className="font-bold text-sm text-emerald-400">Live Sync Complete</h4>
                            <p className="text-xs text-slate-300">Latest data fetched from Official Portal.</p>
                        </div>
                        <button onClick={() => setShowToast(false)} className="ml-2 text-slate-500 hover:text-white">✕</button>
                    </div>
                </div>
            )}

            {/* Upload Modal Overlay */}
            {isUploadOpen && (
                <div className="fixed inset-0 z-50 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
                    <div className="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
                        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" onClick={() => setIsUploadOpen(false)}></div>
                        <span className="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
                        <div className="inline-block align-bottom bg-white rounded-lg px-4 pt-5 pb-4 text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full sm:p-6">
                            <div className="flex justify-between items-center mb-4">
                                <h3 className="text-lg leading-6 font-medium text-gray-900" id="modal-title">Upload Extra Data</h3>
                                <button onClick={() => setIsUploadOpen(false)} className="text-gray-400 hover:text-gray-500">
                                    <span className="sr-only">Close</span>
                                    <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                                    </svg>
                                </button>
                            </div>
                            <FileUpload onDataProcessed={(newData) => {
                                onDataProcessed(newData);
                                setIsUploadOpen(false);
                            }} />
                        </div>
                    </div>
                </div>
            )}

            {/* Header */}
            <header className="bg-white shadow-sm border-b border-slate-200 sticky top-0 z-10">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex flex-col sm:flex-row justify-between items-center gap-4">
                    <div className="flex items-center">
                        <div className="mr-3 border-r border-slate-200 pr-3">
                            {/* UIDAI Logo with fallback */}
                            <img
                                src="https://upload.wikimedia.org/wikipedia/en/thumb/c/cf/Aadhaar_Logo.svg/100px-Aadhaar_Logo.svg.png"
                                alt="Aadhaar"
                                className="h-10 w-auto object-contain"
                                onError={(e) => {
                                    e.currentTarget.style.display = 'none';
                                    const span = document.createElement('span');
                                    span.className = "text-xl font-bold text-red-600";
                                    span.innerText = "UIDAI";
                                    e.currentTarget.parentElement?.appendChild(span);
                                }}
                            />
                        </div>
                        <div>
                            <div className="flex items-center gap-2">
                                <h1 className="text-xl font-bold text-slate-900 leading-none">Satark Intelligence</h1>
                                <span className="bg-indigo-100 text-indigo-700 text-[10px] font-bold px-2 py-0.5 rounded-full border border-indigo-200 uppercase tracking-wide">
                                    Official Partner
                                </span>
                            </div>
                            <p className="text-xs text-slate-500 mt-1 uppercase tracking-wider flex items-center gap-2">
                                Strategic Dashboard
                                {data.processing_time_ms && (
                                    <span className="bg-green-100 text-green-700 px-1.5 py-0.5 rounded text-[10px] font-bold border border-green-200 animate-pulse">
                                        ⚡ {data.processing_time_ms}ms Real-Time
                                    </span>
                                )}
                            </p>
                        </div>
                    </div>

                    <div className="flex items-center gap-4">
                        {/* Auto Sync Indicator */}
                        {isSyncing && (
                            <div className="flex items-center gap-2 px-3 py-1 bg-indigo-50 text-indigo-600 rounded-full border border-indigo-100 text-xs font-semibold animate-pulse">
                                <RefreshCw className="w-3 h-3 animate-spin" />
                                Syncing Real-Time...
                            </div>
                        )}

                        <button
                            onClick={() => setIsUploadOpen(true)}
                            className="bg-indigo-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-indigo-700 transition-colors shadow-sm"
                        >
                            Upload Extra Data
                        </button>

                        <select
                            value={selectedState}
                            onChange={(e) => setSelectedState(e.target.value)}
                            className="block w-48 rounded-md border-0 py-1.5 pl-3 pr-10 text-slate-900 ring-1 ring-inset ring-slate-300 focus:ring-2 focus:ring-indigo-600 sm:text-sm sm:leading-6"
                        >
                            {states.map(s => <option key={s} value={s}>{s}</option>)}
                        </select>

                        <button
                            onClick={() => window.location.reload()}
                            className="text-sm font-medium text-slate-500 hover:text-indigo-600 transition-colors"
                        >
                            Reset
                        </button>
                    </div>
                </div>
            </header>

            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">

                {/* KPI Cards (Active Filters) */}
                <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                    <div onClick={() => setStatusFilter('ALL')} className={`cursor-pointer transition-transform hover:scale-[1.02] ${statusFilter === 'ALL' ? 'ring-2 ring-blue-400 ring-offset-2 rounded-xl' : ''}`}>
                        <StatCard
                            label="Total Pending Updates"
                            value={data.summary.total_pending_updates.toLocaleString()}
                            subtext="National Deficit"
                            icon={Users}
                            color="blue"
                        />
                    </div>
                    <div onClick={() => setStatusFilter(statusFilter === 'CRITICAL' ? 'ALL' : 'CRITICAL')} className={`cursor-pointer transition-transform hover:scale-[1.02] ${statusFilter === 'CRITICAL' ? 'ring-2 ring-red-400 ring-offset-2 rounded-xl' : ''}`}>
                        <StatCard
                            label="Critical Districts"
                            value={data.summary.critical_districts_count}
                            subtext=">50% Gap (Action Needed)"
                            icon={AlertOctagon}
                            color="red"
                        />
                    </div>
                    <div onClick={() => setStatusFilter(statusFilter === 'MODERATE' ? 'ALL' : 'MODERATE')} className={`cursor-pointer transition-transform hover:scale-[1.02] ${statusFilter === 'MODERATE' ? 'ring-2 ring-orange-400 ring-offset-2 rounded-xl' : ''}`}>
                        <StatCard
                            label="Moderate Risk"
                            value={data.districts.filter(d => d.status === 'MODERATE').length}
                            subtext="20-50% Gap"
                            icon={Activity}
                            color="orange"
                        />
                    </div>

                    <div onClick={() => setStatusFilter(statusFilter === 'EMERGING' ? 'ALL' : 'EMERGING')} className={`cursor-pointer transition-transform hover:scale-[1.02] ${statusFilter === 'EMERGING' ? 'ring-2 ring-yellow-400 ring-offset-2 rounded-xl' : ''}`}>
                        <StatCard
                            label="Emerging"
                            value={data.districts.filter(d => d.status === 'SAFE' && d.gap_percentage > 0).length}
                            subtext="1-20% Gap"
                            icon={TrendingUp}
                            color="yellow"
                        />
                    </div>

                    <div onClick={() => setStatusFilter('COMPLIANT')} className={`cursor-pointer transition-transform hover:scale-[1.02] ${statusFilter === 'COMPLIANT' ? 'ring-2 ring-emerald-400 ring-offset-2 rounded-xl' : ''}`}>
                        <StatCard
                            label="Compliant"
                            value={data.districts.filter(d => d.status === 'SAFE' && d.gap_percentage === 0).length}
                            subtext="0% Gap (Perfect)"
                            icon={CheckCircle}
                            color="emerald"
                        />
                    </div>
                </div>

                {/* Charts & Map Area */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    {/* Map: Hero Section */}
                    <div className="lg:col-span-2">
                        <MapVisualizer
                            districts={data.districts}
                            selectedState={selectedState}
                            onDistrictClick={(state) => setSelectedState(state)}
                        />
                    </div>

                    {/* AI Insights & Charts Panel */}
                    <div className="space-y-6">
                        <div className="bg-slate-900 text-white p-6 rounded-xl shadow-lg relative overflow-hidden">
                            <div className="absolute top-0 right-0 -mr-4 -mt-4 w-32 h-32 bg-indigo-500 rounded-full opacity-20 blur-3xl"></div>
                            <div className="relative z-10">
                                <h3 className="text-lg font-semibold mb-4 flex items-center">
                                    <span className="w-2 h-2 bg-green-400 rounded-full mr-2 animate-pulse"></span>
                                    AI Live Insights
                                </h3>

                                <div className="space-y-4 max-h-[400px] overflow-y-auto pr-2 custom-scrollbar">
                                    {/* Show anomalies relevant to filter if possible, else global top 3 */}
                                    {filteredDistricts.filter(d => d.is_anomaly).slice(0, 10).map((d, i) => (
                                        <div key={i} className="bg-white/10 p-4 rounded-lg backdrop-blur-sm border border-white/5">
                                            <p className="text-sm font-medium text-indigo-300 mb-1">Anomaly Detected</p>
                                            <p className="text-sm">
                                                <span className="font-bold text-white">{d.district}</span>: {d.ai_reasoning || `Shows unusual update lag (${d.gap_percentage}%)`}
                                            </p>
                                        </div>
                                    ))}
                                    {filteredDistricts.filter(d => d.is_anomaly).length === 0 && (
                                        <div className="bg-white/10 p-4 rounded-lg backdrop-blur-sm border border-white/5">
                                            <p className="text-sm text-slate-300">No statistical anomalies detected in current view.</p>
                                        </div>
                                    )}
                                </div>

                                <div className="mt-6 pt-6 border-t border-white/10">
                                    <p className="text-xs text-slate-400">
                                        Based on Isolation Forest Algorithm (v2.1)
                                    </p>
                                </div>
                            </div>
                        </div>

                        <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
                            <h3 className="text-sm font-semibold text-slate-800 mb-4">Top Deficit Districts ({selectedState})</h3>
                            <div className="h-[300px] w-full" style={{ height: 300, minHeight: 300 }}>
                                {isMounted && chartData.length > 0 ? (
                                    <ResponsiveContainer width="100%" height="100%">
                                        <BarChart data={chartData} layout="vertical" margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                                            <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} />
                                            <XAxis type="number" hide />
                                            <YAxis dataKey="district" type="category" width={80} tick={{ fontSize: 10 }} />
                                            <Tooltip
                                                contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                                                formatter={(value?: number) => [`${value}% Gap`, 'Deficit']}
                                            />
                                            <Bar dataKey="gap_percentage" fill="#F43F5E" radius={[0, 4, 4, 0]} barSize={15} />
                                        </BarChart>
                                    </ResponsiveContainer>
                                ) : (
                                    <div className="h-full flex flex-col items-center justify-center text-slate-400">
                                        <Activity className="w-8 h-8 mb-2 opacity-20" />
                                        <span className="text-xs">No chart data available</span>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                </div>

                {/* Data Table */}
                <DistrictTable districts={filteredDistricts} />

            </main>

            <ChatWidget />
        </div>
    );
}
