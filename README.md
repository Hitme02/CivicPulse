# CivicPulse Feedback Analyzer(RVU HACKATHOM)

CivicPulse Feedback Analyzer is a Python-based tool designed to process and analyze multilingual civic feedback. It provides insights such as sentiment analysis, urgency detection, topic classification, and priority scoring to help prioritize and address civic issues effectively.

---

## Features

- **Multilingual Support**: Automatically detects the language of the feedback and translates it into English for analysis.
- **Sentiment Analysis**: Classifies feedback as Positive, Negative, or Neutral using advanced NLP models.
- **Urgency Detection**: Identifies urgent feedback based on predefined keywords or context.
- **Topic Classification**: Categorizes feedback into predefined civic topics such as "water supply," "public safety," and "infrastructure."
- **Priority Scoring**: Calculates a priority score based on sentiment and urgency to help prioritize feedback.

---

## Installation

### Prerequisites
- Python 3.11 or higher
- Virtual environment (recommended)

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/Hitme02/CivicPulse.git
   cd CivicPulse
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv civicpulse-env
   source civicpulse-env/bin/activate
3. Install dependencies:
   ```bash
   pip install -r requirements.txt

---
##Usage
1. Activate the virtual environment
   ```bash
   source civicpulse-env/bin/activate
2. Run the feedback analyzer script:
   ```bash
   python sentiment_module.py
3. Modify the test_inputs list in the script to analyze specific feedback.
