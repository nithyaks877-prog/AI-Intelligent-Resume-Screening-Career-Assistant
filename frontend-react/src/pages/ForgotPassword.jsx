import { useState } from "react";
import { Link } from "react-router-dom";
import { Sparkles, Mail } from "lucide-react";
import api from "../api/client";

export default function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setMessage("");
    setLoading(true);

    try {
      const response = await api.post("/auth/forgot-password", { email });
      setMessage(response.data.message);
    } catch (err) {
      setError("Something went wrong. Please try again.");
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

        <h2 className="text-xl font-bold mb-1">Forgot your password?</h2>
        <p className="text-text-secondary text-sm mb-6">
          Enter your email and we'll send you a link to reset it.
        </p>

        {message ? (
          <div className="flex items-start gap-3 bg-status-green-bg text-status-green-text text-sm rounded-xl p-4">
            <Mail className="w-5 h-5 shrink-0 mt-0.5" />
            <p>{message}</p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="text-sm font-medium text-text-primary">
                Email
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="mt-1 w-full px-4 py-3 rounded-xl bg-page-bg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-accent-teal"
                placeholder="alex@university.edu"
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
              {loading ? "Sending..." : "Send Reset Link"}
            </button>
          </form>
        )}

        <p className="text-center text-sm text-text-secondary mt-6">
          <Link to="/" className="text-accent-purple font-medium hover:underline">
            Back to login
          </Link>
        </p>
      </div>
    </div>
  );
}
