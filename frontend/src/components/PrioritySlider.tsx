import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

interface PrioritySliderProps {
  value: number;
  onChange: (value: number) => void;
}

const PrioritySlider: React.FC<PrioritySliderProps> = ({ value, onChange }) => {
  const [localValue, setLocalValue] = useState(value);
  const [isDragging, setIsDragging] = useState(false);

  useEffect(() => {
    setLocalValue(value);
  }, [value]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = parseInt(e.target.value, 10);
    setLocalValue(newValue);
  };

  const handleChangeCommitted = () => {
    onChange(localValue);
    setIsDragging(false);
  };

  return (
    <motion.div 
      className="w-full mb-8"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: 0.2 }}
    >
      <div className="flex items-center justify-between mb-2">
        <label className="text-sm font-medium text-neutral-700">
          Priority Threshold
        </label>
        <motion.div 
          className={`px-3 py-1 rounded-full text-sm font-medium ${
            localValue >= 70
              ? 'bg-error-100 text-error-700'
              : localValue >= 40
              ? 'bg-warning-100 text-warning-700'
              : 'bg-success-100 text-success-700'
          }`}
          animate={{
            backgroundColor: 
              localValue >= 70
                ? 'rgba(254, 226, 226, 1)'
                : localValue >= 40
                ? 'rgba(255, 251, 235, 1)'
                : 'rgba(236, 253, 245, 1)',
            color:
              localValue >= 70
                ? 'rgba(185, 28, 28, 1)'
                : localValue >= 40
                ? 'rgba(180, 83, 9, 1)'
                : 'rgba(4, 120, 87, 1)',
          }}
          transition={{ duration: 0.3 }}
        >
          {localValue}
        </motion.div>
      </div>
      <div className="relative">
        <div className="h-2 bg-neutral-200 rounded-full">
          <motion.div 
            className="absolute h-2 rounded-full bg-gradient-to-r from-success-500 via-warning-500 to-error-500"
            style={{ width: `${localValue}%` }}
            animate={{ width: `${localValue}%` }}
            transition={{ duration: 0.2 }}
          />
        </div>
        <input
          type="range"
          min="0"
          max="100"
          step="10"
          value={localValue}
          onChange={handleChange}
          onMouseDown={() => setIsDragging(true)}
          onMouseUp={handleChangeCommitted}
          onTouchStart={() => setIsDragging(true)}
          onTouchEnd={handleChangeCommitted}
          className="absolute top-0 left-0 w-full h-2 opacity-0 cursor-pointer"
        />
        <motion.div 
          className="absolute top-0 w-4 h-4 bg-white rounded-full shadow-md border-2 border-primary-500 transform -translate-y-1"
          style={{ left: `calc(${localValue}% - 8px)` }}
          animate={{ 
            left: `calc(${localValue}% - 8px)`,
            scale: isDragging ? 1.2 : 1
          }}
          transition={{ duration: 0.2 }}
        />
      </div>
      <div className="flex justify-between mt-1 text-xs text-neutral-500">
        <span>0</span>
        <span>20</span>
        <span>40</span>
        <span>60</span>
        <span>80</span>
        <span>100</span>
      </div>
    </motion.div>
  );
};

export default PrioritySlider;