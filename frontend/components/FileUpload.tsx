import React, { useCallback, useState } from 'react';
import { Upload, FileText, CheckCircle, AlertCircle } from 'lucide-react';
import { uploadFiles, ProcessingResult } from '@/services/api';

interface FileUploadProps {
    onDataProcessed: (data: ProcessingResult) => void;
}

export function FileUpload({ onDataProcessed }: FileUploadProps) {
    const [enrolmentFile, setEnrolmentFile] = useState<File | null>(null);
    const [biometricFile, setBiometricFile] = useState<File | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleProcess = async () => {
        if (!enrolmentFile || !biometricFile) {
            setError("Please select both files.");
            return;
        }
        setLoading(true);
        setError(null);
        try {
            const result = await uploadFiles(enrolmentFile, biometricFile);
            onDataProcessed(result);
        } catch (err) {
            setError("Failed to process files. Ensure they are valid CSVs.");
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const FileZone = ({
        label,
        file,
        setFile,
        accept = ".csv"
    }: {
        label: string,
        file: File | null,
        setFile: (f: File | null) => void,
        accept?: string
    }) => (
        <div className="border-2 border-dashed border-slate-300 rounded-lg p-6 flex flex-col items-center justify-center bg-slate-50 hover:bg-slate-100 transition-colors">
            {file ? (
                <div className="text-center">
                    <CheckCircle className="w-10 h-10 text-emerald-500 mb-2 mx-auto" />
                    <p className="text-sm font-medium text-slate-700">{file.name}</p>
                    <button
                        onClick={() => setFile(null)}
                        className="text-xs text-red-500 hover:text-red-700 mt-2"
                    >
                        Remove
                    </button>
                </div>
            ) : (
                <label className="cursor-pointer text-center w-full h-full block">
                    <Upload className="w-10 h-10 text-slate-400 mb-2 mx-auto" />
                    <p className="text-sm font-medium text-slate-600">{label}</p>
                    <p className="text-xs text-slate-400 mt-1">Drag & drop or click</p>
                    <input
                        type="file"
                        accept={accept}
                        className="hidden"
                        onChange={(e) => {
                            if (e.target.files?.[0]) setFile(e.target.files[0]);
                        }}
                    />
                </label>
            )}
        </div>
    );

    return (
        <div className="w-full max-w-2xl mx-auto bg-white shadow-xl rounded-2xl p-8 border border-slate-200">
            <div className="text-center mb-8">
                <h2 className="text-2xl font-bold text-slate-800">Upload Data Sources</h2>
                <p className="text-slate-500">Provide UIDAI CSV extracts to initialize the Intelligence Engine</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                <FileZone label="Enrolment Data (CSV)" file={enrolmentFile} setFile={setEnrolmentFile} />
                <FileZone label="Biometric Update Data (CSV)" file={biometricFile} setFile={setBiometricFile} />
            </div>

            {error && (
                <div className="mb-4 p-3 bg-red-50 text-red-700 rounded-lg flex items-center text-sm">
                    <AlertCircle className="w-4 h-4 mr-2" />
                    {error}
                </div>
            )}

            <button
                onClick={handleProcess}
                disabled={loading || !enrolmentFile || !biometricFile}
                className={`w-full py-3 rounded-lg font-semibold text-white transition-all shadow-md
            ${loading || !enrolmentFile || !biometricFile
                        ? 'bg-slate-400 cursor-not-allowed'
                        : 'bg-indigo-600 hover:bg-indigo-700 hover:shadow-lg'}`}
            >
                {loading ? (
                    <span className="flex items-center justify-center">
                        <svg className="animate-spin -ml-1 mr-2 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        Processing Intelligence...
                    </span>
                ) : "Initialize Dashboard"}
            </button>
        </div>
    );
}
