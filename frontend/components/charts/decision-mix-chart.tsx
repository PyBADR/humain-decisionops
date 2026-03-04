"use client";

import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from "recharts";

interface DecisionMixChartProps {
  data: {
    approve: number;
    review: number;
    reject: number;
    pending: number;
  };
}

const COLORS = {
  APPROVE: "#22c55e",
  REVIEW: "#f59e0b",
  REJECT: "#ef4444",
  PENDING: "#6b7280",
};

export function DecisionMixChart({ data }: DecisionMixChartProps) {
  const chartData = [
    { name: "Approved", value: data.approve, color: COLORS.APPROVE },
    { name: "Review", value: data.review, color: COLORS.REVIEW },
    { name: "Rejected", value: data.reject, color: COLORS.REJECT },
    { name: "Pending", value: data.pending, color: COLORS.PENDING },
  ].filter((item) => item.value > 0);

  return (
    <ResponsiveContainer width="100%" height={250}>
      <PieChart>
        <Pie
          data={chartData}
          cx="50%"
          cy="50%"
          innerRadius={60}
          outerRadius={90}
          paddingAngle={2}
          dataKey="value"
          label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
          labelLine={false}
        >
          {chartData.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={entry.color} />
          ))}
        </Pie>
        <Tooltip
          contentStyle={{
            backgroundColor: "#1f2937",
            border: "1px solid #374151",
            borderRadius: "8px",
            color: "#f9fafb",
          }}
          formatter={(value: number) => [`${value} claims`, ""]}
        />
        <Legend
          verticalAlign="bottom"
          height={36}
          formatter={(value) => <span style={{ color: "#9ca3af" }}>{value}</span>}
        />
      </PieChart>
    </ResponsiveContainer>
  );
}
