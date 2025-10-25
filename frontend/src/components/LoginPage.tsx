import React from 'react';

interface LoginPageProps {
  onLoginSuccess: () => void;
  onBack: () => void;
}

const LoginPage: React.FC<LoginPageProps> = ({ onLoginSuccess, onBack }) => {
  return (
    <div className="flex flex-col items-center justify-center h-screen bg-gray-100">
      <div className="bg-white p-8 rounded-2xl shadow-lg w-96">
        <h2 className="text-2xl font-semibold text-center mb-6">Login</h2>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            onLoginSuccess();
          }}
          className="space-y-4"
        >
          <input type="email" placeholder="Email" className="w-full p-2 border border-gray-300 rounded" required />
          <input type="password" placeholder="Password" className="w-full p-2 border border-gray-300 rounded" required />
          <button type="submit" className="w-full bg-indigo-600 text-white py-2 rounded hover:bg-indigo-700 transition">
            Login
          </button>
        </form>
        <button onClick={onBack} className="text-indigo-600 text-sm mt-4 hover:underline w-full text-center">
          ← Back to Landing Page
        </button>
      </div>
    </div>
  );
};

export default LoginPage;
