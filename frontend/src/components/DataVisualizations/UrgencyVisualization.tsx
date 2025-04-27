import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { motion } from 'framer-motion';
import { SentimentData, UrgencyLevel } from '../../types';

interface UrgencyVisualizationProps {
  data: SentimentData[];
}

const UrgencyVisualization: React.FC<UrgencyVisualizationProps> = ({ data }) => {
  // Count different urgency levels
  const urgencyCounts = data.reduce<Record<UrgencyLevel, number>>(
    (acc, item) => {
      acc[item.urgency] = (acc[item.urgency] || 0) + 1;
      return acc;
    },
    { high: 0, medium: 0, low: 0 }
  );

  const chartData = [
    { name: 'High', value: urgencyCounts.high, color: '#EF4444' },
    { name: 'Medium', value: urgencyCounts.medium, color: '#F59E0B' },
    { name: 'Low', value: urgencyCounts.low, color: '#10B981' },
  ].filter(item => item.value > 0);

  const renderTooltip = ({ payload }: any) => {
    if (!payload || !payload.length) return null;
    
    const { name, value, color } = payload[0].payload;
    const percentage = ((value / data.length) * 100).toFixed(1);
    
    return (
      <div className="bg-white p-2 shadow-lg rounded border border-neutral-200">
        <p className="font-medium" style={{ color }}>
          {name} Urgency
        </p>
        <p className="text-sm text-neutral-600">
          Count: {value} ({percentage}%)
        </p>
      </div>
    );
  };

  // Group urgency reasons for display
  const urgencyReasons = data.reduce<Record<UrgencyLevel, string[]>>((acc, item) => {
    if (!acc[item.urgency]) {
      acc[item.urgency] = [];
    }
    if (!acc[item.urgency].includes(item.urgency_reason)) {
      acc[item.urgency].push(item.urgency_reason);
    }
    return acc;
  }, { high: [], medium: [], low: [] });

  // If no data
  if (data.length === 0) {
    return (
      <motion.div 
        className="h-64 flex items-center justify-center rounded-lg bg-neutral-50 border border-neutral-200"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
      >
        <p className="text-neutral-500">No urgency data available</p>
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
      <h3 className="text-lg font-medium mb-4">Urgency Distribution</h3>
      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={chartData}
            margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
          >
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip content={renderTooltip} />
            <Bar dataKey="value" radius={[4, 4, 0, 0]}>
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      <motion.div 
        className="mt-8 space-y-4"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <h4 className="text-base font-medium">Urgency Reasons</h4>
        
        {Object.entries(urgencyReasons)
          .filter(([_, reasons]) => reasons.length > 0)
          .map(([level, reasons]) => (
            <div 
              key={level} 
              className={`p-4 rounded-lg ${
                level === 'high' 
                  ? 'bg-error-50 border border-error-200' 
                  : level === 'medium'
                  ? 'bg-warning-50 border border-warning-200'
                  : 'bg-success-50 border border-success-200'
              }`}
            >
              <h5 className={`font-medium ${
                level === 'high' 
                  ? 'text-error-700' 
                  : level === 'medium'
                  ? 'text-warning-700'
                  : 'text-success-700'
              }`}>
                {level.charAt(0).toUpperCase() + level.slice(1)} Urgency
              </h5>
              <ul className="mt-2 space-y-1">
                {reasons.map((reason, i) => (
                  <li key={i} className="text-sm text-neutral-700">
                    • {reason}
                  </li>
                ))}
              </ul>
            </div>
          ))}
      </motion.div>
    </motion.div>
  );
};

export default UrgencyVisualization;