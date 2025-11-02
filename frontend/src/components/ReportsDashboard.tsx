import React from "react";

interface ReportsDashboardProps {
  onBack: () => void;
}

const ReportsDashboard: React.FC<ReportsDashboardProps> = ({ onBack }) => {
  return (
    <div className="w-full md:w-1/2 flex flex-col justify-center items-center bg-white shadow-inner p-8 text-center">
      <h2 className="text-2xl font-semibold mb-4 text-legal-navy">
        Reports Dashboard
      </h2>
      <p className="text-gray-600 mb-6">
        View, download, or generate detailed reports about your submitted cases.
        Monitor progress and connect with trusted legal experts.
      </p>
      <button
        onClick={onBack}
        className="bg-legal-navy text-white px-6 py-2 rounded-lg hover:bg-blue-800 transition"
      >
        ← Back to Chat
      </button>
    </div>
  );
};

export default ReportsDashboard;
