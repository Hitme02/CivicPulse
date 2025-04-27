// Define types for the sentiment analysis data

export type SentimentType = 'positive' | 'negative' | 'neutral';
export type UrgencyLevel = 'high' | 'medium' | 'low';

export interface TopicScore {
  name: string;
  score: number;
}

export interface SentimentData {
  id: string;
  hashtag: string;
  sentiment: SentimentType;
  urgency: UrgencyLevel;
  urgency_reason: string;
  topic: string;
  topic_scores: TopicScore[];
  priority_score: number;
  timestamp: string;
}

export interface ApiResponse {
  data: SentimentData[];
  success: boolean;
  message?: string;
}

export type TabType = 'topic' | 'sentiment' | 'urgency';