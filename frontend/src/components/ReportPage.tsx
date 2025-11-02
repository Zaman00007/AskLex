import React, { useState } from "react";

interface ReportPageProps {
  onBack: () => void;
}

interface Expert {
  name: string;
  experience: number;
  satisfiedClients: number;
  price: string;
  phone: string;
}

const expertsData: Record<string, Expert[]> = {
  Theft: [
    { name: "Ramesh Kumar Singh", experience: 8, satisfiedClients: 320, price: "₹600", phone: "+91 9876543210" },
    { name: "Aditi Tiya Agarwal", experience: 5, satisfiedClients: 210, price: "₹450", phone: "+91 9012345678" },
  ],
  Assault: [
    { name: "Vimlesh Kumar Mandal", experience: 10, satisfiedClients: 400, price: "₹700", phone: "+91 9811122233" },
    { name: "Kumar Aditya Chopra", experience: 6, satisfiedClients: 270, price: "₹500", phone: "+91 9900011122" },
  ],
  Fraud: [
    { name: "Vishnu Nath Tiwari", experience: 12, satisfiedClients: 480, price: "₹850", phone: "+91 9777766666" },
    { name: "Md Shahid Zaman", experience: 7, satisfiedClients: 350, price: "₹600", phone: "+91 8888800000" },
  ],
  Cybercrime: [
    { name: "Sneha Rajput", experience: 9, satisfiedClients: 390, price: "₹650", phone: "+91 9123456789" },
    { name: "Rohit Anand", experience: 6, satisfiedClients: 250, price: "₹500", phone: "+91 9789090909" },
  ],
  Harassment: [
    { name: "Anjali Verma", experience: 11, satisfiedClients: 460, price: "₹800", phone: "+91 9999911111" },
    { name: "Manoj Bhatia", experience: 5, satisfiedClients: 240, price: "₹500", phone: "+91 9112233445" },
  ],
};

const ReportPage: React.FC<ReportPageProps> = ({ onBack }) => {
  const [crimeType, setCrimeType] = useState("");
  const [incident, setIncident] = useState("");
  const [culpritName, setCulpritName] = useState("");
  const [date, setDate] = useState("");
  const [time, setTime] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const [selectedExpert, setSelectedExpert] = useState<Expert | null>(null);
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [paymentDone, setPaymentDone] = useState(false);
  const [message, setMessage] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Assume logged-in email is stored in localStorage
    const email = localStorage.getItem("userEmail");
    if (!email) {
      alert("You must be logged in to report a crime.");
      return;
    }

    try {
      const response = await fetch("http://localhost:5000/report", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email,
          crimeType,
          incident,
          culpritName,
          date,
          time,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        setMessage("✅ Report submitted successfully!");
        setSubmitted(true);
      } else {
        setMessage(`❌ ${data.message || "Failed to submit report"}`);
      }
    } catch (error) {
      console.error("Error submitting report:", error);
      setMessage("⚠️ Server error. Please try again later.");
    }

    setTimeout(() => setMessage(""), 3000);
  };

  const handleChatNow = (expert: Expert) => {
    setSelectedExpert(expert);
    setShowPaymentModal(true);
  };

  const handlePaymentSuccess = () => {
    setPaymentDone(true);
  };

  const handleCloseModal = () => {
    setShowPaymentModal(false);
    setPaymentDone(false);
    setSelectedExpert(null);
  };

  const handleReportAnotherCrime = () => {
    setCrimeType("");
    setIncident("");
    setCulpritName("");
    setDate("");
    setTime("");
    setSubmitted(false);
    setSelectedExpert(null);
    setPaymentDone(false);
  };

  return (
    <div className="flex flex-col md:flex-row h-screen bg-gray-50">
      <div className="w-full md:w-1/2 flex justify-center items-center p-8 relative">
        {!submitted ? (
          <form
            onSubmit={handleSubmit}
            className="bg-white shadow-lg rounded-2xl p-8 w-full max-w-md"
          >
            <h2 className="text-xl font-semibold text-legal-navy mb-4 text-center">
              File a New Report
            </h2>

            {message && (
              <div className="text-center mb-4 text-sm font-medium text-green-600">
                {message}
              </div>
            )}

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
                      Experience: {expert.experience} years
                    </p>
                    <p className="text-gray-600">
                      Satisfied Clients: {expert.satisfiedClients}
                    </p>
                    <p className="text-gray-700 font-semibold mt-2">
                      Chat Price: {expert.price}
                    </p>
                    <button
                      onClick={() => handleChatNow(expert)}
                      className="mt-3 w-full bg-indigo-600 text-white py-2 rounded-lg hover:bg-indigo-700 transition"
                    >
                      Chat Now
                    </button>
                  </div>
                ))}
                <button
                  onClick={handleReportAnotherCrime}
                  className="mt-4 w-full bg-gray-700 text-white py-2 rounded-lg hover:bg-gray-800 transition"
                >
                  Report Another Crime
                </button>
              </div>
            ) : (
              <p className="text-gray-500 text-center">
                No experts found for this crime type.
              </p>
            )}
          </div>
        )}
      </div>

      <div className="w-full md:w-1/2 flex flex-col justify-center items-center bg-white shadow-inner p-8 text-center">
        <h2 className="text-2xl font-semibold mb-4 text-legal-navy">
          Reports Dashboard
        </h2>
        <p className="text-gray-600 mb-6">
          View, download, or generate detailed reports about your submitted
          cases. Monitor progress and connect with trusted legal experts.
        </p>
        <button
          onClick={onBack}
          className="bg-legal-navy text-white px-6 py-2 rounded-lg hover:bg-blue-800 transition"
        >
          ← Back to Chat
        </button>
      </div>

      {showPaymentModal && selectedExpert && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-8 w-80 shadow-lg relative">
            {!paymentDone ? (
              <>
                <h3 className="text-lg font-semibold text-gray-800 mb-4 text-center">
                  Pay {selectedExpert.price} to chat with {selectedExpert.name}
                </h3>
                <p className="text-gray-600 text-sm mb-4 text-center">
                  Secure payment gateway simulation
                </p>
                <button
                  onClick={handlePaymentSuccess}
                  className="w-full bg-green-600 text-white py-2 rounded-lg hover:bg-green-700 transition"
                >
                  Proceed to Pay
                </button>
                <button
                  onClick={handleCloseModal}
                  className="w-full mt-3 bg-gray-300 text-gray-700 py-2 rounded-lg hover:bg-gray-400 transition"
                >
                  Cancel
                </button>
              </>
            ) : (
              <div className="text-center">
                <h3 className="text-lg font-semibold text-green-600 mb-2">
                  ✅ Payment Successful!
                </h3>
                <p className="text-gray-700 mb-3">
                  Expert Contact:{" "}
                  <span className="font-medium">{selectedExpert.phone}</span>
                </p>
                <p className="text-sm text-gray-500 mb-4">
                  You can now call or WhatsApp the expert directly.
                </p>
                <button
                  onClick={handleCloseModal}
                  className="bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition"
                >
                  Close
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ReportPage;
