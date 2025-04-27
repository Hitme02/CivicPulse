import React from 'react';
import { motion } from 'framer-motion';
import { TabType } from '../types';
import clsx from 'clsx';

interface TabNavigationProps {
  activeTab: TabType;
  onChange: (tab: TabType) => void;
}

const TabNavigation: React.FC<TabNavigationProps> = ({ activeTab, onChange }) => {
  const tabs: { id: TabType; label: string }[] = [
    { id: 'topic', label: 'Topic' },
    { id: 'sentiment', label: 'Sentiment' },
    { id: 'urgency', label: 'Urgency' },
  ];

  return (
    <div className="w-full bg-white rounded-lg p-1 shadow-sm mb-6">
      <div className="flex items-center">
        {tabs.map((tab) => (
          <motion.button
            key={tab.id}
            onClick={() => onChange(tab.id)}
            className={clsx(
              'flex-1 relative py-3 px-4 rounded-md text-sm font-medium transition-colors duration-200 focus:outline-none',
              activeTab === tab.id
                ? 'text-primary-700'
                : 'text-neutral-600 hover:text-primary-600'
            )}
            whileTap={{ scale: 0.97 }}
          >
            {tab.label}
            {activeTab === tab.id && (
              <motion.div
                className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary-500 mx-4"
                layoutId="activeTab"
                initial={false}
              />
            )}
          </motion.button>
        ))}
      </div>
    </div>
  );
};

export default TabNavigation;