import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { motion } from 'framer-motion';
import { SentimentData } from '../../types';

interface TopicVisualizationProps {
  data: SentimentData[];
}

const TopicVisualization: React.FC<TopicVisualizationProps> = ({ data }) => {
  // Process data to count topics
  const topicCounts = data.reduce<Record<string, number>>((acc, item) => {
    acc[item.topic] = (acc[item.topic] || 0) + 1;
    return acc;
  }, {});

  const chartData = Object.entries(topicCounts)
    .map(([topic, count]) => ({ topic, count }))
    .sort((a, b) => b.count - a.count);

  // Generate colors for bars
  const colors = [
    '#0070F3', '#6E56CF', '#10B981', '#F59E0B', '#EF4444',
    '#06B6D4', '#8B5CF6', '#F97316', '#EC4899', '#14B8A6'
  ];

  const renderTooltip = ({ payload }: any) => {
    if (!payload || !payload.length) return null;
    
    const { topic, count } = payload[0].payload;
    
    return (
      <div className="bg-white p-2 shadow-lg rounded border border-neutral-200">
        <p className="font-medium">{topic}</p>
        <p className="text-sm text-neutral-600">Count: {count}</p>
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
        <p className="text-neutral-500">No topic data available</p>
      </motion.div>
    );
  }

  return (
    <motion.div 
      className="w-full h-96"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.3 }}
    >
      <h3 className="text-lg font-medium mb-4">Topic Distribution</h3>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={chartData}
          layout="vertical"
          margin={{ top: 5, right: 30, left: 80, bottom: 5 }}
        >
          <XAxis type="number" />
          <YAxis 
            type="category" 
            dataKey="topic" 
            tick={{ fontSize: 12 }}
            width={80}
          />
          <Tooltip content={renderTooltip} />
          <Bar 
            dataKey="count" 
            radius={[0, 4, 4, 0]}
          >
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </motion.div>
  );
};

export default TopicVisualization;