import { ApiResponse, SentimentData } from '../types';

// Set your FastAPI backend URL here
const API_BASE_URL = 'http://localhost:8080';

/**
 * Fetches sentiment data for the given hashtag(s) and priority threshold from FastAPI backend
 * 
 * @param hashtag - The hashtag to track
 * @param priorityThreshold - Priority threshold to filter results (0-100)
 * @returns Promise with sentiment data
 */
export const fetchSentimentData = async (
  hashtag: string, 
  priorityThreshold: number
): Promise<ApiResponse> => {
  try {
    const response = await fetch(`${API_BASE_URL}/search`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        hashtags: [hashtag],
        priority_threshold: priorityThreshold
      })
    });
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching sentiment data:', error);
    return {
      success: false,
      message: 'Failed to fetch sentiment data. Please try again later.',
      data: []
    };
  }
};