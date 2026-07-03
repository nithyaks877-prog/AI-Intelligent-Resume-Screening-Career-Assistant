import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { Target, Zap, LineChart, Sparkles } from "lucide-react";
import { GoogleLogin } from "@react-oauth/google";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const [role, setRole] = useState("student");
  const [isSignup, setIsSignup] = useState(false);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const { login, signup, googleLogin } = useAuth();
  const navigate = useNavigate();

  const handleGoogleSuccess = async (credentialResponse) => {
    setError("");
    try {
      const data = await googleLogin(credentialResponse.credential, role);
      navigate(data.role === "student" ? "/student" : "/recruiter");
    } catch (err) {
      setError("Google sign-in failed. Please try again.");
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      if (isSignup) {
        await signup(name, email, password, role);
      } else {
        await login(email, password);
      }
      navigate(role === "student" ? "/student" : "/recruiter");
    } catch (err) {
      setError(
        err.response?.data?.detail || "Something went wrong. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen grid grid-cols-1 lg:grid-cols-2">
      {/* LEFT PANEL */}
      <div className="hidden lg:flex flex-col justify-center px-16 bg-page-bg">
        <div className="flex items-center gap-2 mb-10">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-accent-teal to-accent-purple flex items-center justify-center">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <span className="font-semibold text-lg">HireLens</span>
        </div>

        <div className="inline-flex items-center gap-2 w-fit px-3 py-1.5 rounded-full bg-white border border-slate-200 text-xs text-text-secondary mb-6">
          <span className="w-1.5 h-1.5 rounded-full bg-accent-teal"></span>
          AI-powered hiring intelligence
        </div>

        <h1 className="text-5xl font-extrabold leading-tight mb-4">
          Land your role.
          <br />
          <span className="bg-gradient-to-r from-accent-teal to-accent-purple bg-clip-text text-transparent">
            Hire the best.
          </span>
        </h1>

        <p className="text-text-secondary text-lg mb-8 max-w-md">
          ATS scoring, skill gap analysis, and AI candidate ranking — one
          platform for students and recruiters.
        </p>

        <div className="flex gap-3 flex-wrap">
          <Pill icon={<Target className="w-4 h-4" />} label="ATS score" />
          <Pill icon={<Zap className="w-4 h-4" />} label="AI ranking" />
          <Pill icon={<LineChart className="w-4 h-4" />} label="Analytics" />
        </div>
      </div>

      {/* RIGHT PANEL - FORM */}
      <div className="flex items-center justify-center px-6 py-12 bg-white">
        <div className="w-full max-w-sm">
          <h2 className="text-2xl font-bold mb-1">
            {isSignup ? "Create your account" : "Welcome back"}
          </h2>
          <p className="text-text-secondary mb-6">
            {isSignup
              ? "Sign up to get started."
              : "Sign in to continue to your dashboard."}
          </p>

          {/* Role Toggle */}
          <div className="flex bg-page-bg rounded-full p-1 mb-6">
            <RoleButton
              active={role === "student"}
              onClick={() => setRole("student")}
              label="Student"
              icon="🎓"
            />
            <RoleButton
              active={role === "recruiter"}
              onClick={() => setRole("recruiter")}
              label="Recruiter"
              icon="💼"
            />
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {isSignup && (
              <div>
                <label className="text-sm font-medium text-text-primary">
                  Full Name
                </label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                  className="mt-1 w-full px-4 py-3 rounded-xl bg-page-bg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-accent-teal"
                  placeholder="Alex Chen"
                />
              </div>
            )}

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

            <div>
              <div className="flex items-center justify-between">
                <label className="text-sm font-medium text-text-primary">
                  Password
                </label>
                {!isSignup && (
                  <Link
                    to="/forgot-password"
                    className="text-xs text-accent-purple font-medium hover:underline"
                  >
                    Forgot password?
                  </Link>
                )}
              </div>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
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
              {loading
                ? "Please wait..."
                : isSignup
                ? "Create Account"
                : `Continue as ${role === "student" ? "Student" : "Recruiter"}`}
            </button>
          </form>

          <div className="flex items-center gap-3 my-5">
            <div className="flex-1 h-px bg-slate-200" />
            <span className="text-xs text-text-secondary">or</span>
            <div className="flex-1 h-px bg-slate-200" />
          </div>

          <div className="flex justify-center">
            <GoogleLogin
              onSuccess={handleGoogleSuccess}
              onError={() => setError("Google sign-in failed. Please try again.")}
              width="100%"
              text={isSignup ? "signup_with" : "continue_with"}
            />
          </div>

          <p className="text-center text-sm text-text-secondary mt-6">
            {isSignup ? "Already have an account?" : "New here?"}{" "}
            <button
              onClick={() => setIsSignup(!isSignup)}
              className="text-accent-purple font-medium hover:underline"
            >
              {isSignup ? "Sign in" : "Create an account"}
            </button>
          </p>
        </div>
      </div>
    </div>
  );
}

function Pill({ icon, label }) {
  return (
    <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-white border border-slate-200 text-sm font-medium">
      {icon}
      {label}
    </div>
  );
}

function RoleButton({ active, onClick, label, icon }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`flex-1 flex items-center justify-center gap-2 py-2.5 rounded-full text-sm font-semibold transition ${
        active
          ? "bg-white shadow text-text-primary"
          : "text-text-secondary"
      }`}
    >
      <span>{icon}</span>
      {label}
    </button>
  );
}

