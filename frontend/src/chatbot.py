import json
import requests
import time
import math

# Config
GROQ_API_KEY = "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"
GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"
MODEL_NAME = "llama3-8b-8192"
BATCH_SIZE = 30  # Number of tweets per Groq request (you can adjust)

# Step 1: Load data.json
def load_feedback_data(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

# Step 2: Prepare text block for one batch
def prepare_text_for_groq(batch_data):
    combined_text = ""
    for idx, item in enumerate(batch_data, 1):
        text = item.get("text", "")
        sentiment = item.get("sentiment", "unknown")
        combined_text += f"({idx}) [{sentiment.upper()}] {text}\n\n"
    return combined_text

# Step 3: Send a batch to Groq (with retry logic)
def analyze_batch_feedback(batch_data):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    batch_text = prepare_text_for_groq(batch_data)

    system_prompt = (
        "You are an expert data analyst for citizen feedback. "
        "Analyze the sentiments and content. Provide a structured report with sections: "
        "1) Overall Sentiment Analysis, 2) Key Topics Discussed, 3) Urgent Issues Highlighted, "
        "4) Hidden Patterns or Anomalies, and 5) Suggestions for Public Service Improvement. "
        "Summarize professionally in English."
    )

    payload = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Here is a batch of citizen feedback data:\n\n{batch_text}"}
        ],
        "model": MODEL_NAME
    }

    while True:
        response = requests.post(GROQ_ENDPOINT, headers=headers, json=payload)

        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        elif response.status_code == 429:
            error_data = response.json()
            wait_time = 20  # Default wait time if not found

            if "error" in error_data and "message" in error_data["error"]:
                msg = error_data["error"]["message"]
                if "try again in" in msg:
                    # Extract the wait seconds from the message
                    try:
                        wait_time = float(msg.split("try again in")[1].split("s")[0].strip())
                    except Exception:
                        pass
            
            print(f"⏳ Rate limit hit. Waiting for {wait_time:.2f} seconds...")
            time.sleep(wait_time + 1)  # Wait slightly longer
        else:
            raise Exception(f"Groq API Error: {response.status_code} {response.text}")

# Step 4: Main Runner with batching
def main():
    try:
        feedback_data = load_feedback_data("data.json")
        total_batches = math.ceil(len(feedback_data) / BATCH_SIZE)
        
        print(f"📦 Total batches to process: {total_batches}")

        all_summaries = []

        for i in range(total_batches):
            start_idx = i * BATCH_SIZE
            end_idx = min(start_idx + BATCH_SIZE, len(feedback_data))
            batch = feedback_data[start_idx:end_idx]

            print(f"🔹 Processing batch {i+1}/{total_batches}... ({len(batch)} tweets)")
            batch_summary = analyze_batch_feedback(batch)
            all_summaries.append(f"### Batch {i+1} Summary ###\n\n{batch_summary}\n\n")

        final_summary = "\n\n".join(all_summaries)

        # Save output to a file
        with open("feedback_summary_report.txt", "w", encoding="utf-8") as f:
            f.write(final_summary)
        
        print("✅ Analysis completed. Summary saved to feedback_summary_report.txt")
    
    except Exception as e:
        print("❌ Error:", e)

if __name__ == "__main__":
    main()
