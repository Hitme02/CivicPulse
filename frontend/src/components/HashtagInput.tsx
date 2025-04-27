import React, { useState, FormEvent } from 'react';
import { motion } from 'framer-motion';
import { FaSearch } from 'react-icons/fa';

interface HashtagInputProps {
  onSubmit: (hashtag: string) => void;
  isLoading: boolean;
}

const HashtagInput: React.FC<HashtagInputProps> = ({ onSubmit, isLoading }) => {
  const [input, setInput] = useState('');

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      // Remove # if user included it
      const sanitizedInput = input.startsWith('#') ? input.substring(1) : input;
      onSubmit(sanitizedInput);
    }
  };

  return (
    <motion.div 
      className="w-full max-w-md mx-auto mb-8"
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <form onSubmit={handleSubmit} className="relative">
        <div className="relative">
          <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-neutral-400">
            #
          </span>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Enter hashtag to track"
            className="w-full py-3 pl-8 pr-12 rounded-full bg-white border border-neutral-200 shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-300 focus:border-primary-300 transition-all"
            disabled={isLoading}
          />
          <button
            type="submit"
            className={`absolute right-2 top-1/2 transform -translate-y-1/2 w-8 h-8 flex items-center justify-center rounded-full transition-all ${
              isLoading
                ? 'bg-neutral-200 text-neutral-400 cursor-not-allowed'
                : 'bg-primary-500 text-white hover:bg-primary-600'
            }`}
            disabled={isLoading}
          >
            {isLoading ? (
              <div className="w-4 h-4 border-2 border-neutral-400 border-t-transparent rounded-full animate-spin" />
            ) : (
              <FaSearch size={14} />
            )}
          </button>
        </div>
      </form>
      <p className="text-xs text-neutral-500 mt-2 text-center">
        Try topics like: technology, climate, politics, sports
      </p>
    </motion.div>
  );
};

export default HashtagInput;