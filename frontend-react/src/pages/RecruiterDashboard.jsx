import { useState, useEffect } from "react";
import { Users, Briefcase, TrendingUp, Star, Upload, Search, Bell, MessageSquare } from "lucide-react";
import Sidebar from "../components/Sidebar";
import { StatCard, DifficultyTag } from "../components/ui";
import WeeklyAnalytics from "../components/WeeklyAnalytics";
import { useAuth } from "../context/AuthContext";
import api from "../api/client";

const PIPELINE_STAGES = ["Applied", "Screening", "Interview", "Assessment", "Hired"];
const STAGE_COLORS = {
  Applied: "bg-slate-100 text-slate-700",
  Screening: "bg-amber-100 text-amber-700",
  Interview: "bg-blue-100 text-blue-700",
  Assessment: "bg-purple-100 text-purple-700",
  Hired: "bg-green-100 text-green-700",
};

export default function RecruiterDashboard() {
  const { user } = useAuth();

  const [roleTitle, setRoleTitle] = useState("");
  const [jdText, setJdText] = useState("");
  const [resumeFiles, setResumeFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);
  const [pipeline, setPipeline] = useState(null);

  const loadPipeline = () => {
    api.get("/recruiter/pipeline").then((res) => {
      setPipeline(res.data);
    }).catch(() => {});
  };

  useEffect(() => {
    loadPipeline();
  }, []);

  const handleAnalyze = async () => {
    if (resumeFiles.length === 0 || !jdText.trim()) {
      setError("Please upload at least one resume and paste a job description.");
      return;
    }

    setError("");
    setLoading(true);

    try {
      const formData = new FormData();
      Array.from(resumeFiles).forEach((file) => {
        formData.append("resumes", file);
      });
      formData.append("job_description", jdText);
      formData.append("role_title", roleTitle || "Untitled Role");

      const response = await api.post("/recruiter/analyze", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      setResult(response.data);
      loadPipeline();
    } catch (err) {
      setError(
        err.response?.data?.detail || "Analysis failed. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  const updateStatus = async (candidateId, newStatus) => {
    const formData = new FormData();
    formData.append("status", newStatus);

    await api.patch(`/recruiter/candidates/${candidateId}/status`, formData);

    // Update local state so the UI reflects the change immediately
    setResult((prev) => ({
      ...prev,
      results: prev.results.map((c) =>
        c.candidate_id === candidateId ? { ...c, status: newStatus } : c
      ),
    }));
    loadPipeline();
  };

  return (
    <div className="flex min-h-screen bg-page-bg">
      <Sidebar role="recruiter" />

      <div className="flex-1">
        {/* Top bar */}
        <div className="flex items-center justify-between px-8 py-4 bg-white border-b border-slate-100">
          <div className="flex items-center gap-2 bg-page-bg rounded-full px-4 py-2 w-96">
            <Search className="w-4 h-4 text-text-secondary" />
            <input
              placeholder="Search applicants, jobs..."
              className="bg-transparent outline-none text-sm w-full"
            />
          </div>
          <div className="flex items-center gap-4">
            <Bell className="w-5 h-5 text-text-secondary" />
            <MessageSquare className="w-5 h-5 text-text-secondary" />
            <div className="w-9 h-9 rounded-full bg-gradient-to-br from-accent-teal to-accent-purple flex items-center justify-center text-white text-sm font-semibold">
              {user?.name?.[0]?.toUpperCase() || "R"}
            </div>
          </div>
        </div>

        <div className="p-8 max-w-6xl mx-auto">
          {/* Header */}
          <div className="mb-6">
            <div className="text-xs font-semibold text-text-secondary tracking-wide uppercase mb-1">
              Recruiter Console
            </div>
            <h1 className="text-2xl font-bold">Hiring Overview</h1>
          </div>

          {/* Upload section */}
          <div className="bg-white rounded-card p-6 border border-slate-100 shadow-sm mb-6">
            <div className="flex items-center gap-2 mb-4">
              <Upload className="w-5 h-5 text-accent-purple" />
              <h2 className="font-semibold">Upload Job Description &amp; Resumes</h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <div>
                <label className="text-sm font-medium block mb-1.5">Role Title</label>
                <input
                  type="text"
                  value={roleTitle}
                  onChange={(e) => setRoleTitle(e.target.value)}
                  placeholder="e.g. Senior Data Scientist"
                  className="w-full text-sm border border-slate-200 rounded-xl px-3 py-2.5 bg-page-bg"
                />
              </div>
              <div>
                <label className="text-sm font-medium block mb-1.5">Candidate Resumes (multiple)</label>
                <input
                  type="file"
                  accept=".pdf,.docx"
                  multiple
                  onChange={(e) => setResumeFiles(e.target.files)}
                  className="w-full text-sm border border-slate-200 rounded-xl px-3 py-2.5 bg-page-bg"
                />
              </div>
            </div>

            <label className="text-sm font-medium block mb-1.5">Job Description</label>
            <textarea
              value={jdText}
              onChange={(e) => setJdText(e.target.value)}
              rows={3}
              placeholder="Paste the full JD here..."
              className="w-full text-sm border border-slate-200 rounded-xl px-3 py-2.5 bg-page-bg resize-none"
            />

            {error && (
              <p className="text-sm text-status-red-text mt-3">{error}</p>
            )}

            <button
              onClick={handleAnalyze}
              disabled={loading}
              className="mt-4 bg-sidebar text-white font-semibold px-5 py-2.5 rounded-xl hover:opacity-90 transition disabled:opacity-50"
            >
              {loading ? "Analyzing Candidates..." : "🚀 Analyze Candidates"}
            </button>
          </div>

          {/* Stat cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <StatCard
              icon={<Users className="w-5 h-5 text-accent-teal" />}
              value={result ? result.total_candidates : pipeline?.total_candidates ?? "—"}
              label="Total Candidates"
              sublabel="This session"
            />
            <StatCard
              icon={<TrendingUp className="w-5 h-5 text-accent-purple" />}
              value={result ? result.average_ats : "—"}
              label="Average ATS"
              sublabel="This session"
            />
            <StatCard
              icon={<Star className="w-5 h-5 text-status-green-text" />}
              value={result ? result.best_candidate : "—"}
              label="Best Candidate"
              sublabel="This session"
            />
            <StatCard
              icon={<Briefcase className="w-5 h-5 text-status-blue-text" />}
              value={result ? result.recommended_count : "—"}
              label="Recommended"
              sublabel="This session"
            />
          </div>

          <WeeklyAnalytics />

          {/* Candidate Ranking */}
          {result && (
            <div className="bg-white rounded-card p-6 border border-slate-100 shadow-sm mb-6">
              <h3 className="font-semibold mb-1">AI Candidate Ranking</h3>
              <p className="text-sm text-text-secondary mb-4">
                Ranked by JD match — {roleTitle || "Untitled Role"}
              </p>

              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="text-left text-xs text-text-secondary uppercase border-b border-slate-100">
                      <th className="pb-2">Candidate</th>
                      <th className="pb-2">AI Score</th>
                      <th className="pb-2">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.results.map((c) => (
                      <tr key={c.candidate_id} className="border-b border-slate-50">
                        <td className="py-3 font-medium">{c.candidate}</td>
                        <td className="py-3">
                          <div className="flex items-center gap-2">
                            <div className="w-24 h-1.5 bg-page-bg rounded-full overflow-hidden">
                              <div
                                className="h-full bg-gradient-to-r from-accent-teal to-accent-purple"
                                style={{ width: `${c.ats_score}%` }}
                              />
                            </div>
                            {c.ats_score}
                          </div>
                        </td>
                        <td className="py-3">
                          <select
                            value={c.status}
                            onChange={(e) => updateStatus(c.candidate_id, e.target.value)}
                            className={`text-xs font-medium rounded-full px-3 py-1.5 border-none outline-none ${STAGE_COLORS[c.status]}`}
                          >
                            {PIPELINE_STAGES.map((stage) => (
                              <option key={stage} value={stage}>{stage}</option>
                            ))}
                          </select>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Candidate Details */}
          {result && (
            <div className="space-y-4">
              {result.results.map((c) => (
                <div key={c.candidate_id} className="bg-white rounded-card p-6 border border-slate-100 shadow-sm">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-semibold">{c.candidate}</h4>
                    <span className="text-sm text-text-secondary">ATS Score: {c.ats_score}/100</span>
                  </div>

                  <div className="mb-3">
                    <div className="text-xs font-semibold text-text-secondary uppercase mb-1">AI Summary</div>
                    <p className="text-sm text-text-secondary">{c.ai_summary}</p>
                  </div>

                  <div className="mb-3">
                    <div className="text-xs font-semibold text-text-secondary uppercase mb-1">Recommendation</div>
                    <p className="text-sm font-medium">{c.recommendation}</p>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                      <div className="text-xs font-semibold text-status-green-text uppercase mb-1.5">Matched Skills</div>
                      <div className="flex flex-wrap gap-1.5">
                        {c.matched_skills.map((s) => (
                          <span key={s} className="text-xs bg-status-green-bg text-status-green-text px-2 py-1 rounded-full">{s}</span>
                        ))}
                      </div>
                    </div>
                    <div>
                      <div className="text-xs font-semibold text-status-red-text uppercase mb-1.5">Missing Skills</div>
                      <div className="flex flex-wrap gap-1.5">
                        {c.missing_skills.map((s) => (
                          <span key={s} className="text-xs bg-status-red-bg text-status-red-text px-2 py-1 rounded-full">{s}</span>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

