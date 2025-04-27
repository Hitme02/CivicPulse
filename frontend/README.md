# Real-time Sentiment Analysis Dashboard

A responsive React application for tracking and visualizing sentiment analysis data in real-time. Users can track hashtags and view sentiment, topic, and urgency analysis with dynamic filtering.

## Features

- **Hashtag Tracking**: Input hashtags to track sentiment across social media.
- **Multi-faceted Analysis**: View data through three different lenses - Topic, Sentiment, and Urgency.
- **Dynamic Filtering**: Filter results using a priority slider (0-100).
- **Real-time Updates**: Results update dynamically as users adjust filters or change tabs.
- **Responsive Design**: Optimized for all devices from mobile to desktop.

## Tech Stack

- React with TypeScript
- Tailwind CSS for styling
- Recharts for data visualization
- Framer Motion for animations

## Getting Started

1. Clone the repository
2. Install dependencies: `npm install`
3. Start the development server: `npm run dev`

## Backend Integration

This frontend is designed to work with a backend that provides sentiment analysis data in the following JSON format:

```json
{
  "data": [
    {
      "id": "unique-id",
      "hashtag": "example",
      "sentiment": "positive | negative | neutral",
      "urgency": "high | medium | low",
      "urgency_reason": "Reason for the urgency level",
      "topic": "Topic name",
      "topic_scores": [
        { "name": "Topic1", "score": 85 },
        { "name": "Topic2", "score": 65 }
      ],
      "priority_score": 75,
      "timestamp": "2023-01-01T12:00:00Z"
    }
  ],
  "success": true
}
```

Currently, the application uses mock data for demonstration purposes. Replace the mock implementation in `src/services/api.ts` with your actual API calls when integrating with a backend.

## License

MIT