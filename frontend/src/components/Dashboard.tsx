import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { TabType, SentimentData } from '../types';
import { fetchSentimentData } from '../services/api';
import HashtagInput from './HashtagInput';
import TabNavigation from './TabNavigation';
import PrioritySlider from './PrioritySlider';
import TopicVisualization from './DataVisualizations/TopicVisualization';
import SentimentVisualization from './DataVisualizations/SentimentVisualization';
import UrgencyVisualization from './DataVisualizations/UrgencyVisualization';
import ResultsTable from './ResultsTable';

const Dashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabType>('topic');
  const [priorityThreshold, setPriorityThreshold] = useState<number>(0);
  const [hashtag, setHashtag] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [data, setData] = useState<SentimentData[]>([]);
  const [error, setError] = useState<string | null>(null);

  // Fetch data when hashtag or priority changes
  useEffect(() => {
    const fetchData = async () => {
      if (!hashtag) return;
      
      setIsLoading(true);
      setError(null);
      
      try {
        const result = await fetchSentimentData(hashtag, priorityThreshold);
        
        if (result.success) {
          setData(result.data);
        } else {
          setError(result.message || 'An error occurred fetching data');
        }
      } catch (err) {
        setError('Failed to fetch sentiment data. Please try again.');
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchData();
  }, [hashtag, priorityThreshold]);

  // Handle hashtag submission
  const handleHashtagSubmit = (newHashtag: string) => {
    setHashtag(newHashtag);
  };

  // Handle tab change
  const handleTabChange = (tab: TabType) => {
    setActiveTab(tab);
  };

  // Handle priority threshold change
  const handlePriorityChange = (value: number) => {
    setPriorityThreshold(value);
  };

  // Render appropriate visualization based on active tab
  const renderVisualization = () => {
    switch (activeTab) {
      case 'topic':
        return <TopicVisualization data={data} />;
      case 'sentiment':
        return <SentimentVisualization data={data} />;
      case 'urgency':
        return <UrgencyVisualization data={data} />;
      default:
        return <TopicVisualization data={data} />;
    }
  };

  return (
    <div className="min-h-screen bg-neutral-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <motion.h1 
            className="text-2xl font-bold text-neutral-900"
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            Sentiment Analysis Dashboard
          </motion.h1>
        </div>
      </header>
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <motion.section 
          className="bg-white rounded-lg shadow-sm p-6 mb-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.1 }}
        >
          <HashtagInput onSubmit={handleHashtagSubmit} isLoading={isLoading} />
          
          {hashtag && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.3 }}
              className="text-center mb-6"
            >
              <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-primary-100 text-primary-800">
                #{hashtag}
              </span>
            </motion.div>
          )}
          
          {error && (
            <motion.div 
              className="bg-error-50 border border-error-200 text-error-700 px-4 py-3 rounded mb-6 text-center"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              {error}
            </motion.div>
          )}
          
          {isLoading ? (
            <div className="flex justify-center py-20">
              <div className="w-12 h-12 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin"></div>
            </div>
          ) : (
            hashtag && data.length > 0 && (
              <>
                <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-6">
                  <div className="md:w-1/3">
                    <TabNavigation activeTab={activeTab} onChange={handleTabChange} />
                  </div>
                  <div className="md:w-2/3">
                    <PrioritySlider value={priorityThreshold} onChange={handlePriorityChange} />
                  </div>
                </div>
                
                <motion.div 
                  className="mt-8"
                  key={activeTab}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.2 }}
                >
                  {renderVisualization()}
                </motion.div>
                
                <ResultsTable data={data} />
              </>
            )
          )}
          
          {!isLoading && hashtag && data.length === 0 && (
            <motion.div 
              className="text-center py-20 bg-neutral-50 rounded-lg"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              <p className="text-neutral-500">No data found for #{hashtag} with the current priority threshold.</p>
              <p className="text-neutral-400 text-sm mt-2">Try lowering the priority threshold or searching for a different hashtag.</p>
            </motion.div>
          )}
          
          {!isLoading && !hashtag && (
            <motion.div 
              className="text-center py-20 bg-neutral-50 rounded-lg"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              <p className="text-neutral-500">Enter a hashtag above to start tracking sentiment data.</p>
              <p className="text-neutral-400 text-sm mt-2">Try topics like technology, climate, politics, or sports.</p>
            </motion.div>
          )}
        </motion.section>
      </main>
      
      <footer className="bg-white border-t border-neutral-200 py-6">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <p className="text-center text-sm text-neutral-500">
            Real-time Sentiment Analysis Dashboard &copy; {new Date().getFullYear()}
          </p>
        </div>
      </footer>
    </div>
  );
};

export default Dashboard;