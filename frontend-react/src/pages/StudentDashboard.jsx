import { useState, useEffect } from "react";
import { Target, Zap, TrendingUp, AlertCircle, Upload, Search, Bell, MessageSquare } from "lucide-react";
import Sidebar from "../components/Sidebar";
import { StatCard, ProgressBar, SkillPill, DifficultyTag } from "../components/ui";
import { useAuth } from "../context/AuthContext";
import api from "../api/client";
import ReactMarkdown from "react-markdown";
export default function StudentDashboard() {
  const { user } = useAuth();

  const [resumeFile, setResumeFile] = useState(null);
  const [jdText, setJdText] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);
  const [historyCount, setHistoryCount] = useState(0);

  useEffect(() => {
    api.get("/student/history").then((res) => {
      setHistoryCount(res.data.length);
    }).catch(() => {});
  }, []);

  const handleAnalyze = async () => {
    if (!resumeFile || !jdText.trim()) {
      setError("Please upload a resume and paste a job description.");
      return;
    }

    setError("");
    setLoading(true);

    try {
      const formData = new FormData();
      formData.append("resume", resumeFile);
      formData.append("job_description", jdText);

      const response = await api.post("/student/analyze", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      setResult(response.data);
      setHistoryCount((c) => c + 1);
    } catch (err) {
      setError(
        err.response?.data?.detail || "Analysis failed. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen bg-page-bg">
      <Sidebar role="student" />

      <div className="flex-1">
        {/* Top bar */}
        <div className="flex items-center justify-between px-8 py-4 bg-white border-b border-slate-100">
          <div className="flex items-center gap-2 bg-page-bg rounded-full px-4 py-2 w-96">
            <Search className="w-4 h-4 text-text-secondary" />
            <input
              placeholder="Search jobs, skills, courses..."
              className="bg-transparent outline-none text-sm w-full"
            />
          </div>
          <div className="flex items-center gap-4">
            <Bell className="w-5 h-5 text-text-secondary" />
            <MessageSquare className="w-5 h-5 text-text-secondary" />
            <div className="w-9 h-9 rounded-full bg-gradient-to-br from-accent-teal to-accent-purple flex items-center justify-center text-white text-sm font-semibold">
              {user?.name?.[0]?.toUpperCase() || "U"}
            </div>
          </div>
        </div>

        <div className="p-8 max-w-6xl mx-auto">
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <div>
              <div className="text-xs font-semibold text-text-secondary tracking-wide uppercase mb-1">
                Welcome back
              </div>
              <h1 className="text-2xl font-bold">
                Hi {user?.name || "there"} — let's boost your resume 🚀
              </h1>
            </div>
          </div>

          {/* Upload section */}
          <div className="bg-white rounded-card p-6 border border-slate-100 shadow-sm mb-6">
            <div className="flex items-center gap-2 mb-4">
              <Upload className="w-5 h-5 text-accent-purple" />
              <h2 className="font-semibold">Upload Resume &amp; Job Description</h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium block mb-1.5">Resume (PDF/DOCX)</label>
                <input
                  type="file"
                  accept=".pdf,.docx"
                  onChange={(e) => setResumeFile(e.target.files[0])}
                  className="w-full text-sm border border-slate-200 rounded-xl px-3 py-2.5 bg-page-bg"
                />
              </div>
              <div>
                <label className="text-sm font-medium block mb-1.5">Job Description</label>
                <textarea
                  value={jdText}
                  onChange={(e) => setJdText(e.target.value)}
                  rows={1}
                  placeholder="Paste the JD here..."
                  className="w-full text-sm border border-slate-200 rounded-xl px-3 py-2.5 bg-page-bg resize-none h-[42px]"
                />
              </div>
            </div>

            {error && (
              <p className="text-sm text-status-red-text mt-3">{error}</p>
            )}

            <button
              onClick={handleAnalyze}
              disabled={loading}
              className="mt-4 bg-sidebar text-white font-semibold px-5 py-2.5 rounded-xl hover:opacity-90 transition disabled:opacity-50"
            >
              {loading ? "Analyzing..." : "🚀 Analyze Resume"}
            </button>
          </div>

          {/* Stat cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <StatCard
              icon={<Target className="w-5 h-5 text-accent-teal" />}
              value={result ? `${result.ats_score}/100` : "—"}
              label="ATS Score"
              sublabel={result ? "From latest scan" : "Run an analysis"}
            />
            <StatCard
              icon={<Zap className="w-5 h-5 text-accent-purple" />}
              value={result ? `${result.match_percentage}%` : "—"}
              label="Skill Match"
              sublabel="vs. this job description"
            />
            <StatCard
              icon={<TrendingUp className="w-5 h-5 text-status-green-text" />}
              value={historyCount}
              label="Resumes Analyzed"
              sublabel="All time"
            />
            <StatCard
              icon={<AlertCircle className="w-5 h-5 text-status-red-text" />}
              value={result ? result.missing_skills.length : "—"}
              label="Skill Gaps"
              sublabel="To close for this role"
            />
          </div>

          {result && (
            <>
              {/* ATS Breakdown + Skills Analysis */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
                <div className="bg-white rounded-card p-6 border border-slate-100 shadow-sm">
                  <h3 className="font-semibold mb-4">ATS Score Breakdown</h3>
                  {Object.entries(result.breakdown).map(([label, value]) => {
                    // Each category has a different max score, so we
                    // normalize to a real percentage instead of showing
                    // the raw point value with a misleading "%" sign.
                    const maxScores = {
                      "Skill Match": 40,
                      "Projects": 20,
                      "Education": 15,
                      "Certifications": 10,
                      "Resume Quality": 10,
                      "Content Relevance": 5,
                    };
                    const max = maxScores[label] || 100;
                    const percentage = Math.round((value / max) * 100);

                    return (
                      <ProgressBar
                        key={label}
                        label={label}
                        percentage={percentage}
                      />
                    );
                  })}
                </div>

                <div className="bg-white rounded-card p-6 border border-slate-100 shadow-sm">
                  <h3 className="font-semibold mb-4">Skills Analysis</h3>
                  <div className="text-xs font-semibold text-text-secondary uppercase mb-2">
                    Present
                  </div>
                  <div className="flex flex-wrap gap-2 mb-4">
                    {result.matched_skills.map((skill) => (
                      <SkillPill key={skill} label={skill} present />
                    ))}
                  </div>
                  <div className="text-xs font-semibold text-text-secondary uppercase mb-2">
                    Missing
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {result.missing_skills.map((skill) => (
                      <SkillPill key={skill} label={skill} present={false} />
                    ))}
                  </div>
                </div>
              </div>

              {/* Learning Plan + Interview Questions */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
                <div className="bg-white rounded-card p-6 border border-slate-100 shadow-sm">
                  <h3 className="font-semibold mb-1">Personalized Learning Plan</h3>
                  <p className="text-sm text-text-secondary mb-4">
                    Curated to close your top gaps
                  </p>
                  <div className="space-y-3">
                    {result.learning_plan.length === 0 && (
                      <p className="text-sm text-text-secondary">
                        No gaps found — great match!
                      </p>
                    )}
                    {result.learning_plan.map((course, i) => (
                      <div
                        key={i}
                        className="flex items-center justify-between border border-slate-100 rounded-xl px-4 py-3"
                      >
                        <div>
                          <div className="font-medium text-sm">{course.title}</div>
                          <div className="text-xs text-text-secondary">
                            {course.platform} · {course.duration}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="bg-white rounded-card p-6 border border-slate-100 shadow-sm">
                  <h3 className="font-semibold mb-1">AI Interview Questions</h3>
                  <p className="text-sm text-text-secondary mb-4">
                    Tailored to your target role
                  </p>
                  <div className="space-y-3">
                    {result.interview_questions.map((q, i) => (
                      <div
                        key={i}
                        className="border border-slate-100 rounded-xl px-4 py-3"
                      >
                        <div className="flex items-start gap-3 mb-2">
                          <div className="w-6 h-6 rounded-full bg-page-bg flex items-center justify-center text-xs font-semibold shrink-0">
                            {i + 1}
                          </div>
                          <p className="text-sm font-medium">{q.question}</p>
                        </div>
                        <div className="flex gap-2 ml-9">
                          <span className="text-xs bg-page-bg px-2 py-1 rounded-full">
                            {q.category}
                          </span>
                          <DifficultyTag difficulty={q.difficulty} />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* AI Feedback */}
              <div className="bg-white rounded-card p-6 border border-slate-100 shadow-sm">
                <h3 className="font-semibold mb-3">🤖 AI Resume Feedback</h3>
                <div className="text-sm text-text-secondary prose prose-sm max-w-none prose-headings:font-semibold prose-headings:text-text-primary prose-headings:mt-4 prose-headings:mb-2 prose-strong:text-text-primary">
                    <ReactMarkdown>{result.feedback}</ReactMarkdown>
                </div>
            </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
