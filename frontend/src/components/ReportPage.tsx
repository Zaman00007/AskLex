import React, { useState } from "react";

interface ReportPageProps {
  onBack: () => void;
}

interface Expert {
  name: string;
  experience: number;
  satisfiedClients: number;
  price: string;
}

const expertsData: Record<string, Expert[]> = {
  Theft: [
    { name: "Ramesh Kumar Singh", experience: 8, satisfiedClients: 320, price: "₹600" },
    { name: "Aditi Tiya Agarwal", experience: 5, satisfiedClients: 210, price: "₹450" },
  ],
  Assault: [
    { name: "Vimlesh Kumar Mandal", experience: 10, satisfiedClients: 400, price: "₹700" },
    { name: "Kumar Aditya Chopra", experience: 6, satisfiedClients: 270, price: "₹500" },
  ],
  Fraud: [
    { name: "Vishnu Nath Tiwari", experience: 12, satisfiedClients: 480, price: "₹850" },
    { name: "Md Shahid Zaman", experience: 7, satisfiedClients: 350, price: "₹600" },
  ],
  "Cybercrime": [
    { name: "Sneha Rajput", experience: 9, satisfiedClients: 390, price: "₹650" },
    { name: "Rohit Anand", experience: 6, satisfiedClients: 250, price: "₹500" },
  ],
  Harassment: [
    { name: "Anjali Verma", experience: 11, satisfiedClients: 460, price: "₹800" },
    { name: "Manoj Bhatia", experience: 5, satisfiedClients: 240, price: "₹500" },
  ],
};

const ReportPage: React.FC<ReportPageProps> = ({ onBack }) => {
  const [crimeType, setCrimeType] = useState("");
  const [incident, setIncident] = useState("");
  const [culpritName, setCulpritName] = useState("");
  const [date, setDate] = useState("");
  const [time, setTime] = useState("");
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitted(true);
  };

  return (
    <div className="flex flex-col md:flex-row h-screen bg-gray-50">
      {/* Left Section */}
      <div className="w-full md:w-1/2 flex justify-center items-center p-8">
        {!submitted ? (
          <form
            onSubmit={handleSubmit}
            className="bg-white shadow-lg rounded-2xl p-8 w-full max-w-md"
          >
            <h2 className="text-xl font-semibold text-legal-navy mb-4 text-center">
              File a New Report
            </h2>

            <label className="block text-gray-700 text-sm font-medium mb-2">
              Type of Crime
            </label>
            <select
              value={crimeType}
              onChange={(e) => setCrimeType(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 mb-4 focus:ring-2 focus:ring-blue-500"
              required
            >
              <option value="">Select crime type</option>
              <option value="Theft">Theft</option>
              <option value="Assault">Assault</option>
              <option value="Fraud">Fraud</option>
              <option value="Cybercrime">Cybercrime</option>
              <option value="Harassment">Harassment</option>
            </select>

            <label className="block text-gray-700 text-sm font-medium mb-2">
              Incident Details
            </label>
            <textarea
              value={incident}
              onChange={(e) => setIncident(e.target.value)}
              placeholder="Describe what happened..."
              className="w-full border border-gray-300 rounded-lg px-3 py-2 mb-4 focus:ring-2 focus:ring-blue-500"
              rows={3}
              required
            ></textarea>

            <label className="block text-gray-700 text-sm font-medium mb-2">
              Name of Culprit
            </label>
            <input
              type="text"
              value={culpritName}
              onChange={(e) => setCulpritName(e.target.value)}
              placeholder="Enter name of the culprit"
              className="w-full border border-gray-300 rounded-lg px-3 py-2 mb-4 focus:ring-2 focus:ring-blue-500"
              required
            />

            <div className="flex space-x-4 mb-4">
              <div className="flex-1">
                <label className="block text-gray-700 text-sm font-medium mb-2">
                  Date
                </label>
                <input
                  type="date"
                  value={date}
                  onChange={(e) => setDate(e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              <div className="flex-1">
                <label className="block text-gray-700 text-sm font-medium mb-2">
                  Time
                </label>
                <input
                  type="time"
                  value={time}
                  onChange={(e) => setTime(e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              className="w-full bg-legal-navy text-white py-2 rounded-lg hover:bg-blue-800 transition"
            >
              Submit Report
            </button>
          </form>
        ) : (
          <div className="bg-white shadow-lg rounded-2xl p-8 w-full max-w-md">
            <h2 className="text-xl font-semibold text-legal-navy mb-4 text-center">
              Recommended Legal Experts
            </h2>

            {crimeType && expertsData[crimeType] ? (
              <div className="space-y-4">
                {expertsData[crimeType].map((expert, i) => (
                  <div
                    key={i}
                    className="border border-gray-200 rounded-lg p-4 shadow-sm hover:shadow-md transition"
                  >
                    <h3 className="text-lg font-semibold text-gray-800">
                      {expert.name}
                    </h3>
                    <p className="text-gray-600">
                      Experience: <span className="font-medium">{expert.experience}</span> years
                    </p>
                    <p className="text-gray-600">
                      Satisfied Clients:{" "}
                      <span className="font-medium">{expert.satisfiedClients}</span>
                    </p>
                    <p className="text-gray-700 font-semibold mt-2">
                      Chat Price: {expert.price}
                    </p>
                    <button className="mt-3 w-full bg-indigo-600 text-white py-2 rounded-lg hover:bg-indigo-700 transition">
                      Chat Now
                    </button>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center">
                No experts found for this crime type.
              </p>
            )}
          </div>
        )}
      </div>

      {/* Right Section */}
      <div className="w-full md:w-1/2 flex flex-col justify-center items-center bg-white shadow-inner p-8 text-center">
        <h2 className="text-2xl font-semibold mb-4 text-legal-navy">
          Reports Dashboard
        </h2>
        <p className="text-gray-600 mb-6">
          View, download, or generate detailed reports about your submitted
          cases. You can monitor case progress and track trends of crimes
          reported through our platform.
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
