"use client";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";

interface ClaimsTrendChartProps {
  data: Array<{
    date: string;
    claims: number;
    approved: number;
    rejected: number;
  }>;
}

export function ClaimsTrendChart({ data }: ClaimsTrendChartProps) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
        <XAxis
          dataKey="date"
          stroke="#9ca3af"
          tick={{ fill: "#9ca3af" }}
          tickLine={{ stroke: "#4b5563" }}
        />
        <YAxis
          stroke="#9ca3af"
          tick={{ fill: "#9ca3af" }}
          tickLine={{ stroke: "#4b5563" }}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: "#1f2937",
            border: "1px solid #374151",
            borderRadius: "8px",
            color: "#f9fafb",
          }}
        />
        <Legend
          verticalAlign="top"
          height={36}
          formatter={(value) => <span style={{ color: "#9ca3af" }}>{value}</span>}
        />
        <Line
          type="monotone"
          dataKey="claims"
          name="Total Claims"
          stroke="#3b82f6"
          strokeWidth={2}
          dot={{ fill: "#3b82f6", strokeWidth: 2 }}
          activeDot={{ r: 6 }}
        />
        <Line
          type="monotone"
          dataKey="approved"
          name="Approved"
          stroke="#22c55e"
          strokeWidth={2}
          dot={{ fill: "#22c55e", strokeWidth: 2 }}
        />
        <Line
          type="monotone"
          dataKey="rejected"
          name="Rejected"
          stroke="#ef4444"
          strokeWidth={2}
          dot={{ fill: "#ef4444", strokeWidth: 2 }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
