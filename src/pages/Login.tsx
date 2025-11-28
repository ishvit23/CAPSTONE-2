import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { LogIn, Loader2 } from "lucide-react";
import { API_BASE_URL } from "@/config";
import { useAuth } from "@/hooks/useAuth";

const Login = () => {
  const navigate = useNavigate();
  const { user, loading } = useAuth();
  const [isRedirecting, setIsRedirecting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!loading && user) {
      navigate("/chat", { replace: true });
    }
  }, [user, loading, navigate]);

  const handleGoogleSignIn = async () => {
    setError(null);
    setIsRedirecting(true);
    try {
      const response = await fetch(`${API_BASE_URL}/auth/google/login/`);
      if (!response.ok) {
        throw new Error("Unable to start Google login");
      }
      const data = await response.json();
      window.location.href = data.auth_url;
    } catch (err) {
      console.error(err);
      setIsRedirecting(false);
      setError("Failed to connect to Google. Please try again.");
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-50 flex items-center justify-center p-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md bg-white rounded-3xl shadow-2xl p-8 text-center"
      >
        <div className="mb-6">
          <div className="w-20 h-20 mx-auto bg-gradient-to-br from-purple-500 to-blue-500 text-white rounded-full flex items-center justify-center text-4xl shadow-lg">
            🤖
          </div>
          <h1 className="text-2xl font-bold text-gray-800 mt-4">
            Welcome to DigiBuddy
          </h1>
          <p className="text-gray-500 mt-2">
            Sign in with Google to continue to your mental health companion.
          </p>
        </div>

        <button
          onClick={handleGoogleSignIn}
          disabled={isRedirecting || loading}
          className="w-full flex items-center justify-center gap-2 bg-gradient-to-r from-red-500 via-pink-500 to-orange-500 text-white font-semibold py-3 rounded-2xl hover:shadow-lg transition-all disabled:opacity-60"
        >
          {isRedirecting ? (
            <Loader2 className="animate-spin" size={20} />
          ) : (
            <LogIn size={20} />
          )}
          {isRedirecting ? "Redirecting to Google..." : "Continue with Google"}
        </button>

        {error && (
          <p className="text-red-500 text-sm mt-4 bg-red-50 p-2 rounded-lg">
            {error}
          </p>
        )}

        <p className="text-xs text-gray-400 mt-6">
          By signing in you agree to our friendly guidelines. We never use your
          data for advertising.
        </p>
      </motion.div>
    </div>
  );
};

export default Login;

