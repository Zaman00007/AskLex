import React from 'react';

interface LandingPageProps {
  onLogin: () => void;
  onRegister: () => void;
}

const LandingPage: React.FC<LandingPageProps> = ({ onLogin, onRegister }) => {
  return (
    <div className="flex flex-col items-center justify-center h-screen bg-gradient-to-br from-blue-100 to-indigo-200">
      <div className="text-center mb-10">
        <h1 className="text-5xl font-bold text-indigo-700 mb-2">Welcome to Legal Chat AI</h1>
        <p className="text-gray-700 text-lg">Your intelligent legal assistant</p>
      </div>
      <div className="flex space-x-6">
        <button
          onClick={onLogin}
          className="bg-indigo-600 text-white px-8 py-3 rounded-lg hover:bg-indigo-700 transition font-semibold"
        >
          Login
        </button>
        <button
          onClick={onRegister}
          className="bg-white text-indigo-700 border-2 border-indigo-600 px-8 py-3 rounded-lg hover:bg-indigo-50 transition font-semibold"
        >
          Register New Account
        </button>
      </div>
    </div>
  );
};

export default LandingPage;
