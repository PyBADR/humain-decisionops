"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";

interface FraudScenariosChartProps {
  data: Array<{
    name: string;
    hits: number;
    category: string;
  }>;
}

const CATEGORY_COLORS: Record<string, string> = {
  Identity: "#8b5cf6",
  Financial: "#f59e0b",
  Collision: "#ef4444",
  Vendor: "#ec4899",
  Medical: "#14b8a6",
  Timing: "#6366f1",
  Policy: "#f97316",
  Document: "#eab308",
  Network: "#dc2626",
};

export function FraudScenariosChart({ data }: FraudScenariosChartProps) {
  const sortedData = [...data].sort((a, b) => b.hits - a.hits).slice(0, 8);

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart
        data={sortedData}
        layout="vertical"
        margin={{ top: 5, right: 30, left: 100, bottom: 5 }}
      >
        <CartesianGrid strokeDasharray="3 3" stroke="#374151" horizontal={false} />
        <XAxis
          type="number"
          stroke="#9ca3af"
          tick={{ fill: "#9ca3af" }}
          tickLine={{ stroke: "#4b5563" }}
        />
        <YAxis
          type="category"
          dataKey="name"
          stroke="#9ca3af"
          tick={{ fill: "#9ca3af", fontSize: 12 }}
          tickLine={{ stroke: "#4b5563" }}
          width={95}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: "#1f2937",
            border: "1px solid #374151",
            borderRadius: "8px",
            color: "#f9fafb",
          }}
          formatter={(value: number, name: string, props: any) => [
            `${value} hits`,
            props.payload.category,
          ]}
        />
        <Bar dataKey="hits" radius={[0, 4, 4, 0]}>
          {sortedData.map((entry, index) => (
            <Cell
              key={`cell-${index}`}
              fill={CATEGORY_COLORS[entry.category] || "#6b7280"}
            />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
