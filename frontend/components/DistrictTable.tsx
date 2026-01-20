import { useState } from 'react';
import { Download, AlertTriangle, CheckCircle, Clock, Eye } from 'lucide-react';
import { DistrictData, downloadReport } from '@/services/api';
import { ReportModal } from './ReportModal';

interface DistrictTableProps {
    districts: DistrictData[];
}

export function DistrictTable({ districts }: DistrictTableProps) {
    const [selectedDistrict, setSelectedDistrict] = useState<DistrictData | null>(null);
    const [isModalOpen, setIsModalOpen] = useState(false);

    const handleDownloadReport = (district: DistrictData) => {
        downloadReport(district);
    };

    const handleViewReport = (district: DistrictData) => {
        setSelectedDistrict(district);
        setIsModalOpen(true);
    };

    const getStatusBadge = (status: string) => {
        switch (status) {
            case 'CRITICAL':
                return (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                        <AlertTriangle className="w-3 h-3 mr-1" /> Critical
                    </span>
                );
            case 'MODERATE':
                return (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                        <Clock className="w-3 h-3 mr-1" /> Moderate
                    </span>
                );
            default:
                return (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800">
                        <CheckCircle className="w-3 h-3 mr-1" /> Safe
                    </span>
                );
        }
    };

    return (
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
            <div className="px-6 py-4 border-b border-slate-200">
                <h3 className="text-lg font-semibold text-slate-800">District-wise Breakdown</h3>
            </div>
            <div className="overflow-x-auto max-h-[500px] overflow-y-auto custom-scrollbar">
                <table className="min-w-full divide-y divide-slate-200">
                    <thead className="bg-slate-50 sticky top-0 z-10 shadow-sm">
                        <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider bg-slate-50">District</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider bg-slate-50">State</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider bg-slate-50">Pending (Gap)</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider bg-slate-50">Gap %</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider bg-slate-50">Status</th>
                            <th className="px-6 py-3 text-right text-xs font-medium text-slate-500 uppercase tracking-wider bg-slate-50">Action</th>
                        </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-slate-200">
                        {districts.map((district, idx) => (
                            <tr key={`${district.state}-${district.district}-${idx}`} className="hover:bg-slate-50 transition-colors">
                                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-slate-900">
                                    {district.district}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500">
                                    {district.state}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500">
                                    {district.pending_updates.toLocaleString()}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500">
                                    <div className="w-full max-w-[100px] h-2 bg-slate-100 rounded-full overflow-hidden">
                                        <div
                                            className={`h-full ${district.gap_percentage > 50 ? 'bg-red-500' : district.gap_percentage > 20 ? 'bg-yellow-400' : 'bg-emerald-500'}`}
                                            style={{ width: `${district.gap_percentage}%` }}
                                        />
                                    </div>
                                    <span className="text-xs mt-1 block">{district.gap_percentage}%</span>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                    {getStatusBadge(district.status)}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-2">
                                    <button
                                        onClick={() => handleViewReport(district)}
                                        className="text-indigo-600 hover:text-indigo-900 inline-flex items-center px-2 py-1 bg-indigo-50 hover:bg-indigo-100 rounded transition-colors"
                                    >
                                        <Eye className="w-3.5 h-3.5 mr-1.5" /> View
                                    </button>
                                    <button
                                        onClick={() => handleDownloadReport(district)}
                                        className="text-slate-600 hover:text-slate-900 inline-flex items-center px-2 py-1 hover:bg-slate-100 rounded transition-colors"
                                    >
                                        <Download className="w-3.5 h-3.5 mr-1.5" /> PDF
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            <ReportModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                district={selectedDistrict}
            />
        </div>
    );
}
