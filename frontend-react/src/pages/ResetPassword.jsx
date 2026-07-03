import { useState } from "react";
import { useSearchParams, useNavigate, Link } from "react-router-dom";
import { Sparkles, CheckCircle } from "lucide-react";
import api from "../api/client";

export default function ResetPassword() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const token = searchParams.get("token");

  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (!token) {
      setError("This reset link is missing its token. Please request a new one.");
      return;
    }

    if (newPassword !== confirmPassword) {
      setError("Passwords don't match.");
      return;
    }

    if (newPassword.length < 6) {
      setError("Password must be at least 6 characters.");
      return;
    }

    setLoading(true);

    try {
      await api.post("/auth/reset-password", {
        token,
        new_password: newPassword,
      });
      setSuccess(true);
      setTimeout(() => navigate("/"), 2500);
    } catch (err) {
      setError(
        err.response?.data?.detail || "This reset link is invalid or has expired."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-page-bg px-6">
      <div className="w-full max-w-sm bg-white rounded-card p-8 border border-slate-100 shadow-sm">
        <div className="flex items-center gap-2 mb-6">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-accent-teal to-accent-purple flex items-center justify-center">
            <Sparkles className="w-4 h-4 text-white" />
          </div>
          <span className="font-semibold">HireLens</span>
        </div>

        {success ? (
          <div className="flex flex-col items-center text-center py-6">
            <CheckCircle className="w-12 h-12 text-status-green-text mb-3" />
            <h2 className="text-lg font-bold mb-1">Password reset!</h2>
            <p className="text-text-secondary text-sm">
              Redirecting you to login...
            </p>
          </div>
        ) : (
          <>
            <h2 className="text-xl font-bold mb-1">Set a new password</h2>
            <p className="text-text-secondary text-sm mb-6">
              Choose a new password for your account.
            </p>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="text-sm font-medium text-text-primary">
                  New Password
                </label>
                <input
                  type="password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  required
                  className="mt-1 w-full px-4 py-3 rounded-xl bg-page-bg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-accent-teal"
                  placeholder="••••••••"
                />
              </div>

              <div>
                <label className="text-sm font-medium text-text-primary">
                  Confirm New Password
                </label>
                <input
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                  className="mt-1 w-full px-4 py-3 rounded-xl bg-page-bg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-accent-teal"
                  placeholder="••••••••"
                />
              </div>

              {error && (
                <p className="text-sm text-status-red-text bg-status-red-bg px-3 py-2 rounded-lg">
                  {error}
                </p>
              )}

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-sidebar text-white font-semibold py-3 rounded-xl hover:opacity-90 transition disabled:opacity-50"
              >
                {loading ? "Resetting..." : "Reset Password"}
              </button>
            </form>

            <p className="text-center text-sm text-text-secondary mt-6">
              <Link to="/" className="text-accent-purple font-medium hover:underline">
                Back to login
              </Link>
            </p>
          </>
        )}
      </div>
    </div>
  );
}
