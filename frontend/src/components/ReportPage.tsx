import React from 'react';

interface ReportPageProps {
  onBack: () => void;
}

const ReportPage: React.FC<ReportPageProps> = ({ onBack }) => {
  return (
    <div className="flex flex-col items-center justify-center h-screen bg-gray-50">
      <div className="bg-white shadow-lg rounded-2xl p-8 w-3/4 max-w-2xl text-center">
        <h2 className="text-2xl font-semibold mb-4 text-legal-navy">Reports Dashboard</h2>
        <p className="text-gray-600 mb-6">
          Here you can view, download, or generate reports for your legal cases.
        </p>
        <button
          onClick={onBack}
          className="bg-legal-navy text-white px-6 py-2 rounded-lg hover:bg-blue-800 transition"
        >
          ← Back to Chat
        </button>
      </div>
    </div>
  );
};

export default ReportPage;
