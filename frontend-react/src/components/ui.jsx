export function StatCard({ icon, label, value, sublabel, badge }) {
  return (
    <div className="bg-white rounded-card p-5 border border-slate-100 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <div className="w-10 h-10 rounded-full bg-page-bg flex items-center justify-center">
          {icon}
        </div>
        {badge && (
          <span className="text-xs font-medium text-status-green-text bg-status-green-bg px-2 py-1 rounded-full">
            {badge}
          </span>
        )}
      </div>
      <div className="text-3xl font-bold">{value}</div>
      <div className="text-sm text-text-secondary mt-1">{label}</div>
      {sublabel && (
        <div className="text-xs text-text-secondary mt-0.5">{sublabel}</div>
      )}
    </div>
  );
}

export function ProgressBar({ label, percentage }) {
  return (
    <div className="mb-4 last:mb-0">
      <div className="flex justify-between text-sm mb-1.5">
        <span className="font-medium">{label}</span>
        <span className="font-semibold">{percentage}%</span>
      </div>
      <div className="w-full h-2 bg-page-bg rounded-full overflow-hidden">
        <div
          className="h-full bg-gradient-to-r from-accent-teal to-accent-purple rounded-full"
          style={{ width: `${Math.min(percentage, 100)}%` }}
        />
      </div>
    </div>
  );
}

export function SkillPill({ label, present }) {
  return (
    <span
      className={`inline-flex items-center gap-1 px-3 py-1.5 rounded-full text-sm font-medium ${
        present
          ? "bg-status-green-bg text-status-green-text"
          : "bg-status-red-bg text-status-red-text"
      }`}
    >
      {present ? "✓" : "✕"} {label}
    </span>
  );
}

export function DifficultyTag({ difficulty }) {
  const styles = {
    Easy: "bg-status-green-bg text-status-green-text",
    Medium: "bg-status-blue-bg text-status-blue-text",
    Hard: "bg-status-red-bg text-status-red-text",
  };
  return (
    <span
      className={`text-xs font-medium px-2 py-1 rounded-full ${
        styles[difficulty] || "bg-status-gray-bg text-status-gray-text"
      }`}
    >
      {difficulty}
    </span>
  );
}
