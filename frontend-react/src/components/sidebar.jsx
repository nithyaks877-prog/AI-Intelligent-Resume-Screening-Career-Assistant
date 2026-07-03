import { LayoutGrid, FileText, Sparkles, BookOpen, MessageSquare, Settings, LogOut, Users, Briefcase, Calendar, Star, BarChart3 } from "lucide-react";
import { useAuth } from "../context/AuthContext";

const studentNav = [
  { label: "Dashboard", icon: LayoutGrid, active: true },
  { label: "My Resume", icon: FileText },
  { label: "AI Suggestions", icon: Sparkles },
  { label: "Learning Plan", icon: BookOpen },
  { label: "Interview Prep", icon: MessageSquare },
  { label: "Settings", icon: Settings },
];

const recruiterNav = [
  { label: "Dashboard", icon: LayoutGrid, active: true },
  { label: "Candidates", icon: Users },
  { label: "Job Listings", icon: Briefcase },
  { label: "Interviews", icon: Calendar },
  { label: "Shortlist", icon: Star },
  { label: "Analytics", icon: BarChart3 },
  { label: "Settings", icon: Settings },
];

export default function Sidebar({ role = "student" }) {
  const { logout } = useAuth();
  const navItems = role === "recruiter" ? recruiterNav : studentNav;

  return (
    <div className="w-64 min-h-screen bg-sidebar text-white flex flex-col justify-between py-6 px-4">
      <div>
        <div className="flex items-center gap-2 px-2 mb-8">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-accent-teal to-accent-purple flex items-center justify-center">
            <Sparkles className="w-4 h-4 text-white" />
          </div>
          <div>
            <div className="font-semibold text-sm leading-none">HireLens</div>
            <div className="text-xs text-slate-400 uppercase tracking-wide">
              {role}
            </div>
          </div>
        </div>

        <nav className="space-y-1">
          {navItems.map(({ label, icon: Icon, active }) => (
            <button
              key={label}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition ${
                active
                  ? "bg-accent-teal text-sidebar"
                  : "text-slate-300 hover:bg-white/5"
              }`}
            >
              <Icon className="w-4 h-4" />
              {label}
            </button>
          ))}
        </nav>
      </div>

      <button
        onClick={logout}
        className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium text-slate-300 hover:bg-white/5 transition"
      >
        <LogOut className="w-4 h-4" />
        Sign out
      </button>
    </div>
  );
}
