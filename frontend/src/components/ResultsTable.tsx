import React from 'react';
import { motion } from 'framer-motion';
import { SentimentData } from '../types';

interface ResultsTableProps {
  data: SentimentData[];
}

const ResultsTable: React.FC<ResultsTableProps> = ({ data }) => {
  // Format date string to more readable format
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleString();
  };

  // Get color for sentiment
  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case 'positive':
        return 'bg-success-100 text-success-800';
      case 'negative':
        return 'bg-error-100 text-error-800';
      case 'neutral':
        return 'bg-neutral-100 text-neutral-800';
      default:
        return 'bg-neutral-100 text-neutral-800';
    }
  };

  // Get color for urgency
  const getUrgencyColor = (urgency: string) => {
    switch (urgency) {
      case 'high':
        return 'bg-error-100 text-error-800';
      case 'medium':
        return 'bg-warning-100 text-warning-800';
      case 'low':
        return 'bg-success-100 text-success-800';
      default:
        return 'bg-neutral-100 text-neutral-800';
    }
  };

  if (data.length === 0) {
    return (
      <motion.div 
        className="mt-8 text-center py-10 bg-neutral-50 rounded-lg border border-neutral-200"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
      >
        <p className="text-neutral-500">No data available. Try adjusting the priority threshold or search for a different hashtag.</p>
      </motion.div>
    );
  }

  return (
    <motion.div 
      className="mt-8 overflow-hidden rounded-lg border border-neutral-200 bg-white"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-neutral-200">
          <thead className="bg-neutral-50">
            <tr>
              <th
                scope="col"
                className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider"
              >
                Topic
              </th>
              <th
                scope="col"
                className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider"
              >
                Sentiment
              </th>
              <th
                scope="col"
                className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider"
              >
                Urgency
              </th>
              <th
                scope="col"
                className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider"
              >
                Priority
              </th>
              <th
                scope="col"
                className="px-6 py-3 text-left text-xs font-medium text-neutral-500 uppercase tracking-wider"
              >
                Timestamp
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-neutral-200">
            {data.map((item) => (
              <motion.tr 
                key={item.id}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.2 }}
              >
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-neutral-900">
                    {item.topic}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span
                    className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getSentimentColor(
                      item.sentiment
                    )}`}
                  >
                    {item.sentiment.charAt(0).toUpperCase() + item.sentiment.slice(1)}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span
                    className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getUrgencyColor(
                      item.urgency
                    )}`}
                  >
                    {item.urgency.charAt(0).toUpperCase() + item.urgency.slice(1)}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div 
                    className={`text-sm font-medium ${
                      item.priority_score >= 70
                        ? 'text-error-600'
                        : item.priority_score >= 40
                        ? 'text-warning-600'
                        : 'text-success-600'
                    }`}
                  >
                    {item.priority_score}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-neutral-500">
                  {formatDate(item.timestamp)}
                </td>
              </motion.tr>
            ))}
          </tbody>
        </table>
      </div>
    </motion.div>
  );
};

export default ResultsTable;