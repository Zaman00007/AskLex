import React, { useEffect, useState } from "react";

interface ReportsDashboardProps {
  onBack: () => void;
  refreshTrigger?: number;
}

interface Report {
  email: string;
  crimeType: string;
  incident: string;
  culpritName: string;
  date: string;
  time: string;
}

const ReportsDashboard: React.FC<ReportsDashboardProps> = ({ onBack, refreshTrigger }) => {
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState(true);
  const userEmail = localStorage.getItem("userEmail");

  const fetchReports = () => {
    if (!userEmail) return;
    setLoading(true);

    fetch(`http://localhost:5000/api/reports?email=${userEmail}`)
      .then((res) => res.json())
      .then((data) => {
        setReports(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Error fetching reports:", err);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchReports();
  }, [refreshTrigger]); // reload when trigger changes

  const handleCloseReport = (index: number) => {
    const report = reports[index];
    fetch("http://localhost:5000/api/close-report", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(report),
    })
      .then((res) => res.json())
      .then((data) => {
        alert(data.message);
        setReports((prev) => prev.filter((_, i) => i !== index));
      })
      .catch((err) => console.error("Error closing report:", err));
  };

  return (
    <div className="w-full md:w-1/2 flex flex-col justify-center items-center bg-white shadow-inner p-8 text-center">
      <h2 className="text-2xl font-semibold mb-4 text-legal-navy">Reports Dashboard</h2>
      {loading ? (
        <p>Loading reports...</p>
      ) : reports.length === 0 ? (
        <p>No reports found.</p>
      ) : (
        <div className="w-full">
          {reports.map((r, i) => (
            <div key={i} className="border p-4 mb-3 rounded-lg bg-gray-50 shadow-sm text-left">
              <p><strong>Crime Type:</strong> {r.crimeType}</p>
              <p><strong>Incident:</strong> {r.incident}</p>
              <p><strong>Culprit Name:</strong> {r.culpritName}</p>
              <p><strong>Date:</strong> {r.date}</p>
              <p><strong>Time:</strong> {r.time}</p>
              <button
                onClick={() => handleCloseReport(i)}
                className="mt-2 bg-red-600 text-white px-4 py-1 rounded hover:bg-red-700"
              >
                Close Report
              </button>
            </div>
          ))}
        </div>
      )}
      <button
        onClick={onBack}
        className="mt-6 bg-legal-navy text-white px-6 py-2 rounded-lg hover:bg-blue-800 transition"
      >
        ← Back to Chat
      </button>
    </div>
  );
};

export default ReportsDashboard;
