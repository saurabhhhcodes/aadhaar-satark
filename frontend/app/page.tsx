'use client';

import React, { useState, useEffect } from 'react';
import { ErrorBoundary } from '@/components/ErrorBoundary';
import { Dashboard } from '@/components/Dashboard';
import { ProcessingResult, fetchInitialData } from '@/services/api';

export default function Home() {
  const [data, setData] = useState<ProcessingResult | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        const result = await fetchInitialData();
        setData(result);
      } catch (err) {
        console.error("Failed to load initial data", err);
      } finally {
        setIsLoading(false);
      }
    };
    loadData();
  }, []);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <ErrorBoundary>
      <main className="min-h-screen bg-slate-50">
        <Dashboard data={data} onDataProcessed={setData} />
      </main>
    </ErrorBoundary>
  );
}
