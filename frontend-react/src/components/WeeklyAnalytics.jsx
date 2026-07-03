import { useState, useEffect } from "react";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import { TrendingUp } from "lucide-react";
import api from "../api/client";

const METRICS = [
  { key: "applications", label: "Applications" },
  { key: "avg_ats", label: "Avg. ATS score" },
];

export default function WeeklyAnalytics() {
  const [data, setData] = useState(null);
  const [activeMetric, setActiveMetric] = useState("applications");

  useEffect(() => {
    api.get("/recruiter/analytics").then((res) => {
      setData(res.data);
    }).catch(() => {});
  }, []);

  if (!data) return null;

  const chartData = data.daily.map((d) => ({
    day: new Date(d.date).toLocaleDateString("en-US", { weekday: "short" }),
    applications: d.applications,
    avg_ats: d.avg_ats,
  }));

  const totalApplications = data.total_this_week;

  return (
    <div className="bg-white rounded-card p-6 border border-slate-100 shadow-sm mb-6">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="font-semibold">Weekly Analytics</h3>
          <p className="text-sm text-text-secondary">
            Real trends from your last 7 days of activity
          </p>
        </div>
        <span className="flex items-center gap-1 text-sm font-medium text-status-green-text">
          <TrendingUp className="w-4 h-4" />
          {data.shortlist_rate}% shortlist rate
        </span>
      </div>

      {/* Metric tabs */}
      <div className="inline-flex bg-page-bg rounded-full p-1 mb-4">
        {METRICS.map((m) => (
          <button
            key={m.key}
            onClick={() => setActiveMetric(m.key)}
            className={`px-4 py-1.5 rounded-full text-sm font-medium transition ${
              activeMetric === m.key
                ? "bg-white shadow text-text-primary"
                : "text-text-secondary"
            }`}
          >
            {m.label}
          </button>
        ))}
      </div>

      {totalApplications === 0 ? (
        <p className="text-sm text-text-secondary py-8 text-center">
          No candidates analyzed in the last 7 days yet.
        </p>
      ) : (
        <>
          <div className="text-3xl font-bold mb-4">
            {totalApplications}
            <span className="text-sm font-normal text-text-secondary ml-2">
              total this week
            </span>
          </div>

          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={chartData}>
              <XAxis
                dataKey="day"
                axisLine={false}
                tickLine={false}
                tick={{ fontSize: 12, fill: "#64748B" }}
              />
              <YAxis hide />
              <Tooltip />
              <Line
                type="monotone"
                dataKey={activeMetric}
                stroke="#22D3EE"
                strokeWidth={2}
                dot={{ fill: "#A78BFA", r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>

          <div className="grid grid-cols-2 gap-4 mt-4 pt-4 border-t border-slate-100">
            <div>
              <div className="text-xs text-text-secondary">Shortlist rate</div>
              <div className="font-semibold">{data.shortlist_rate}%</div>
            </div>
            <div>
              <div className="text-xs text-text-secondary">Week peak</div>
              <div className="font-semibold">{data.week_peak}</div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
