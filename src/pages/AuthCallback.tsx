import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { Loader2, TriangleAlert } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";

const AuthCallback = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { setAuthTokens } = useAuth();
  const [status, setStatus] = useState<"loading" | "error">("loading");

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const error = params.get("error");
    const access = params.get("access");
    const refresh = params.get("refresh");

    if (error) {
      setStatus("error");
      return;
    }

    if (access && refresh) {
      setAuthTokens({ access, refresh });
      navigate("/chat", { replace: true });
    } else {
      setStatus("error");
    }
  }, [location.search, navigate, setAuthTokens]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-50 via-purple-50 to-blue-50 p-6">
      <div className="bg-white rounded-3xl shadow-2xl p-8 text-center max-w-sm w-full">
        {status === "loading" ? (
          <>
            <Loader2 className="mx-auto mb-4 animate-spin text-purple-500" size={40} />
            <h2 className="text-xl font-semibold text-gray-800">Signing you in…</h2>
            <p className="text-gray-500 mt-2">
              We’re completing the secure sign-in and redirecting you back to your chat.
            </p>
          </>
        ) : (
          <>
            <TriangleAlert className="mx-auto mb-4 text-red-500" size={40} />
            <h2 className="text-xl font-semibold text-gray-800">Login failed</h2>
            <p className="text-gray-500 mt-2">
              We couldn’t complete the Google sign-in. Please go back and try again.
            </p>
            <button
              onClick={() => navigate("/login")}
              className="mt-6 px-6 py-2 rounded-full bg-gradient-to-r from-purple-500 to-blue-500 text-white font-semibold"
            >
              Return to login
            </button>
          </>
        )}
      </div>
    </div>
  );
};

export default AuthCallback;

