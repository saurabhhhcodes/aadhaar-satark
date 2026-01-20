import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';

export interface DistrictData {
    state: string;
    district: string;
    lat?: number;
    lng?: number;
    efficiency_index?: number;
    expected_updates: number;
    actual_updates: number;
    pending_updates: number;
    gap_percentage: number;
    status: 'CRITICAL' | 'MODERATE' | 'SAFE';
    is_anomaly: boolean;
    ai_reasoning?: string;
}

export interface DashboardSummary {
    total_pending_updates: number;
    critical_districts_count: number;
    processed_districts: number;
}

export interface ProcessingResult {
    summary: DashboardSummary;
    districts: DistrictData[];
    dataset_info?: {
        enrolment_records: number;
        biometric_records: number;
        source: string;
    };
    error?: string;
    processing_time_ms?: number;
}

export const fetchInitialData = async (): Promise<ProcessingResult> => {
    try {
        const response = await axios.get(`${API_BASE_URL}/initial-data`);
        return response.data;
    } catch (error) {
        console.error('Error fetching initial data:', error);
        throw error;
    }
};

export const uploadFiles = async (
    enrolmentFile: File,
    biometricFile: File
): Promise<ProcessingResult> => {
    const formData = new FormData();
    formData.append('enrolment_file', enrolmentFile);
    formData.append('biometric_file', biometricFile);

    try {
        const response = await axios.post(`${API_BASE_URL}/upload`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    } catch (error) {
        console.error("Upload error:", error);
        throw error;
    }
};

export const downloadReport = async (district: DistrictData) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/generate-report`, district, {
            responseType: 'blob', // Important for PDF download
        });

        // Trigger download
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `Report_${district.district}.pdf`);
        document.body.appendChild(link);
        link.click();
        link.remove();
    } catch (error) {
        console.error("Report download error:", error);
        throw error;
    }
};
