// API service to handle backend communication
import { ApiResponse, SentimentData } from '../types';

// Mock API endpoint - In a real app, replace with actual API URL
const API_BASE_URL = '/https://680da917c47cb8074d90e0e8.mockapi.io/rvu1/:endpoint';

/**
 * Fetches sentiment data for the given hashtag
 * 
 * @param hashtag - The hashtag to track
 * @param priorityThreshold - Priority threshold to filter results (0-100)
 * @returns Promise with sentiment data
 */
export const fetchSentimentData = async (
  hashtag: string, 
  priorityThreshold: number
): Promise<ApiResponse> => {
  // In a real application, this would make an actual API call
  // For demo purposes, we're mocking the response
  
  try {
    // Simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 800));
    
    // This would be replaced with a real fetch call:
    // const response = await fetch(`${API_BASE_URL}/sentiment?hashtag=${hashtag}&priority=${priorityThreshold}`);
    // return await response.json();
    
    return {
      success: true,
      data: generateMockData(hashtag, priorityThreshold)
    };
  } catch (error) {
    console.error('Error fetching sentiment data:', error);
    return {
      success: false,
      message: 'Failed to fetch sentiment data. Please try again later.',
      data: []
    };
  }
};

/**
 * Generates mock sentiment data for demo purposes
 * In a real application, this would be replaced with actual API responses
 */
const generateMockData = (hashtag: string, priorityThreshold: number): SentimentData[] => {
  const sentiments: SentimentType[] = ['positive', 'negative', 'neutral'];
  const urgencyLevels: UrgencyLevel[] = ['high', 'medium', 'low'];
  const topics = ['Politics', 'Entertainment', 'Technology', 'Sports', 'Health', 'Finance', 'Environment'];
  
  // Generate between 15-25 data points
  const count = Math.floor(Math.random() * 11) + 15;
  const results: SentimentData[] = [];
  
  for (let i = 0; i < count; i++) {
    const priority = Math.floor(Math.random() * 101); // 0-100
    
    // Only include if it meets the priority threshold
    if (priority >= priorityThreshold) {
      const sentiment = sentiments[Math.floor(Math.random() * sentiments.length)];
      const urgency = urgencyLevels[Math.floor(Math.random() * urgencyLevels.length)];
      const topic = topics[Math.floor(Math.random() * topics.length)];
      
      // Generate 2-4 topic scores
      const topicScoreCount = Math.floor(Math.random() * 3) + 2;
      const topicScores: TopicScore[] = [];
      
      for (let j = 0; j < topicScoreCount; j++) {
        const randomTopic = topics[Math.floor(Math.random() * topics.length)];
        if (!topicScores.find(t => t.name === randomTopic)) {
          topicScores.push({
            name: randomTopic,
            score: Math.floor(Math.random() * 100) + 1
          });
        }
      }
      
      // Ensure the main topic has the highest score
      const mainTopicExists = topicScores.find(t => t.name === topic);
      if (!mainTopicExists) {
        topicScores.push({
          name: topic,
          score: Math.floor(Math.random() * 30) + 70 // 70-100
        });
      } else {
        mainTopicExists.score = Math.floor(Math.random() * 30) + 70; // 70-100
      }
      
      // Generate a plausible timestamp within the last 24 hours
      const now = new Date();
      const pastTime = new Date(now.getTime() - Math.floor(Math.random() * 24 * 60 * 60 * 1000));
      
      results.push({
        id: `${hashtag}-${i}`,
        hashtag: hashtag,
        sentiment: sentiment,
        urgency: urgency,
        urgency_reason: getUrgencyReason(urgency),
        topic: topic,
        topic_scores: topicScores,
        priority_score: priority,
        timestamp: pastTime.toISOString()
      });
    }
  }
  
  return results;
};

/**
 * Returns a reason string for the given urgency level
 */
const getUrgencyReason = (urgency: UrgencyLevel): string => {
  switch (urgency) {
    case 'high':
      return 'Rapidly increasing mentions and engagement';
    case 'medium':
      return 'Steady growth in discussion volume';
    case 'low':
      return 'Minimal activity or change in engagement';
    default:
      return 'Unknown reason';
  }
};