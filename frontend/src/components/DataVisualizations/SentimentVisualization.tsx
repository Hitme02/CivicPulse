import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import { motion } from 'framer-motion';
import { SentimentData, SentimentType } from '../../types';

interface SentimentVisualizationProps {
  data: SentimentData[];
}

const SentimentVisualization: React.FC<SentimentVisualizationProps> = ({ data }) => {
  // Count different sentiments
  const sentimentCounts = data.reduce<Record<SentimentType, number>>(
    (acc, item) => {
      acc[item.sentiment] = (acc[item.sentiment] || 0) + 1;
      return acc;
    },
    { positive: 0, negative: 0, neutral: 0 }
  );

  const chartData = [
    { name: 'Positive', value: sentimentCounts.positive, color: '#10B981' },
    { name: 'Neutral', value: sentimentCounts.neutral, color: '#6B7280' },
    { name: 'Negative', value: sentimentCounts.negative, color: '#EF4444' },
  ].filter(item => item.value > 0);

  const COLORS = ['#10B981', '#6B7280', '#EF4444'];

  const renderTooltip = ({ payload }: any) => {
    if (!payload || !payload.length) return null;
    
    const { name, value, color } = payload[0].payload;
    const percentage = ((value / data.length) * 100).toFixed(1);
    
    return (
      <div className="bg-white p-2 shadow-lg rounded border border-neutral-200">
        <p className="font-medium" style={{ color }}>
          {name}
        </p>
        <p className="text-sm text-neutral-600">
          Count: {value} ({percentage}%)
        </p>
      </div>
    );
  };

  // If no data
  if (data.length === 0) {
    return (
      <motion.div 
        className="h-64 flex items-center justify-center rounded-lg bg-neutral-50 border border-neutral-200"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
      >
        <p className="text-neutral-500">No sentiment data available</p>
      </motion.div>
    );
  }

  return (
    <motion.div 
      className="w-full"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.3 }}
    >
      <h3 className="text-lg font-medium mb-4">Sentiment Distribution</h3>
      <div className="h-96">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              labelLine={false}
              outerRadius={120}
              innerRadius={60}
              paddingAngle={2}
              dataKey="value"
              label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
            >
              {chartData.map((entry, index) => (
                <Cell 
                  key={`cell-${index}`} 
                  fill={entry.color} 
                />
              ))}
            </Pie>
            <Tooltip content={renderTooltip} />
            <Legend verticalAlign="bottom" height={36} />
          </PieChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4">
        <motion.div 
          className="p-4 rounded-lg bg-success-50 border border-success-200"
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.1 }}
        >
          <div className="text-xl font-semibold text-success-700">
            {sentimentCounts.positive}
          </div>
          <div className="text-sm text-success-600">Positive Mentions</div>
        </motion.div>

        <motion.div 
          className="p-4 rounded-lg bg-neutral-50 border border-neutral-200"
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          <div className="text-xl font-semibold text-neutral-700">
            {sentimentCounts.neutral}
          </div>
          <div className="text-sm text-neutral-600">Neutral Mentions</div>
        </motion.div>

        <motion.div 
          className="p-4 rounded-lg bg-error-50 border border-error-200"
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.3 }}
        >
          <div className="text-xl font-semibold text-error-700">
            {sentimentCounts.negative}
          </div>
          <div className="text-sm text-error-600">Negative Mentions</div>
        </motion.div>
      </div>
    </motion.div>
  );
};

export default SentimentVisualization;