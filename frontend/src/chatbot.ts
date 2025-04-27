// Knowledge base from text file
const knowledgeBase = `
### Batch 1 Summary ###

**Overall Sentiment Analysis**

The overall sentiment of the citizens' feedback batch is overwhelmingly positive, with 62% of the posts expressing appreciation and gratitude towards public servants, government officials, and community leaders for their efforts in providing public service.

**Key Topics Discussed**

1. Public Service: The concept of public service is the most frequently discussed topic, with citizens expressing appreciation and gratitude towards individuals and organizations providing public service.
2. Government Officials: Government officials, particularly ministers, are mentioned in several posts, highlighting their efforts in promoting public service and community development.
3. Community Development: The importance of community development and collaboration is emphasized in several posts, with a focus on initiatives and projects aimed at improving the quality of life for citizens.
4. Innovation: The need for innovation in public service is highlighted in a few posts, with a focus on technology and digital solutions to improve efficiency and effectiveness.
5. Accountability: Accountability and transparency are emphasized in several posts, with citizens calling for greater transparency and accountability from public servants and government officials.

[... rest of your content ...]

### Batch 11 Summary ###

**Structured Report: Analysis of Citizen Feedback Data**

**1. Overall Sentiment Analysis**

The overall sentiment of the provided citizen feedback data is neutral, with a mix of positive, negative, and neutral statements. The data includes opinions on political issues, civic engagement, and patriotism, which are aggregated to provide an overall neutral sentiment.

**2. Key Topics Discussed**

The key topics discussed in the provided citizen feedback data are:

* Politics and governance (democracy, one-man rule, one-party rule, and military rule in Ghana)
* Patriotism and its impact on national unity and divides
* Politicians' speech and responsibility (Rahul Gandhi's statement about freedom fighters)
* Civic engagement and public discourse

**3. Urgent Issues Highlighted**

The citizen feedback data highlights the following urgent issues:

* Concerns about the rejection of alternative forms of governance, such as one-man rule, one-party rule, and military rule, in favor of democracy in Ghana
* The importance of responsible speech and avoiding divisive narratives in political discourse
* The need for politicians to respect historical figures and freedom fighters, and not use their statements to create controversy

**4. Hidden Patterns or Anomalies**

The data does not reveal any significant hidden patterns or anomalies, as the topics and sentiments discussed are largely consistent with public opinions on political issues.

**5. Suggestions for Public Service Improvement**

Based on the analysis, the following suggestions are made for public service improvement:

* Encourage political leaders to prioritize responsible speech and avoid divisive narratives, promoting national unity and respect for historical figures
* Foster an environment that values civic engagement and public discourse, allowing citizens to express their opinions and contributions
* Promote democratic values and principles, encouraging citizens to participate in the democratic process and hold their leaders accountable
* Ensure the government is transparent and accountable to its citizens, reducing corruption and improving the delivery of public services
`;

// Groq API configuration
const GROQ_API_KEY = "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";
const GROQ_API_URL = 'https://api.groq.com/openai/v1/chat/completions';
const GROQ_MODEL = 'llama3-70b-8192'; // You can change to other models as needed

async function getGroqResponse(query: string) {
  try {
    const response = await fetch(GROQ_API_URL, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${GROQ_API_KEY}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: GROQ_MODEL,
        messages: [
          {
            role: 'system',
            content: 'You are CivicPulse, a helpful assistant for civic engagement topics. Provide concise, informative answers about community issues, local governance, and public services.'
          },
          {
            role: 'user',
            content: query
          }
        ],
        max_tokens: 300,
        temperature: 0.7
      })
    });

    if (!response.ok) {
      throw new Error('Failed to get response from Groq API');
    }

    const data = await response.json();
    return data.choices[0].message.content;
  } catch (error) {
    console.error('Error calling Groq API:', error);
    return getFallbackResponse(query);
  }
}

function getFallbackResponse(query: string) {
  const lower = query.toLowerCase();
  for (const kb of knowledgeBase) {
    if (kb.keywords.some(k => lower.includes(k))) {
      return kb.answer;
    }
  }
  return "Sorry, I couldn't find a matching topic. Try asking about education, health, transport, etc.";
}

function createChatbotUI() {
  const btn = document.createElement('button');
  btn.id = 'chatbot-toggle-btn';
  btn.innerHTML = '💬';
  document.body.appendChild(btn);

  const overlay = document.createElement('div');
  overlay.id = 'chatbot-overlay';
  overlay.style.display = 'none';

  const popup = document.createElement('div');
  popup.id = 'chatbot-popup';
  popup.innerHTML = `
    <div id="chatbot-header">
      Chat with CivicPulse
      <button id="chatbot-close-btn">&times;</button>
    </div>
    <div id="chatbot-messages"></div>
    <form id="chatbot-form">
      <input id="chatbot-input" type="text" placeholder="Ask me anything..." autocomplete="off" />
      <button type="submit" id="chatbot-send-btn">&#9658;</button>
    </form>
  `;

  overlay.appendChild(popup);
  document.body.appendChild(overlay);

  btn.onclick = () => {
    overlay.style.display = 'flex';
    btn.style.display = 'none';
  };

  overlay.addEventListener('click', (e) => {
    if (e.target === overlay) {
      overlay.style.display = 'none';
      btn.style.display = 'block';
    }
  });

  document.getElementById('chatbot-close-btn')!.onclick = () => {
    overlay.style.display = 'none';
    btn.style.display = 'block';
  };

  const messages = document.getElementById('chatbot-messages')!;
  const input = document.getElementById('chatbot-input') as HTMLInputElement;
  const form = document.getElementById('chatbot-form') as HTMLFormElement;

  function addMessage(text: string, sender: 'user' | 'bot') {
    const msg = document.createElement('div');
    msg.className = `chatbot-message ${sender}`;
    msg.innerHTML = `<div class="chatbot-bubble">${text}</div>`;
    messages.appendChild(msg);
    messages.scrollTop = messages.scrollHeight;
  }

  // Show a typing indicator while waiting for the API response
  function showTypingIndicator() {
    const indicator = document.createElement('div');
    indicator.id = 'typing-indicator';
    indicator.className = 'chatbot-message bot';
    indicator.innerHTML = '<div class="chatbot-bubble typing">...</div>';
    messages.appendChild(indicator);
    messages.scrollTop = messages.scrollHeight;
    return indicator;
  }

  function removeTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    if (indicator) {
      indicator.remove();
    }
  }

  form.onsubmit = async (e) => {
    e.preventDefault();
    const userInput = input.value.trim();
    if (!userInput) return;
    
    addMessage(userInput, 'user');
    input.value = '';
    
    const typingIndicator = showTypingIndicator();
    
    try {
      const botResponse = await getGroqResponse(userInput);
      removeTypingIndicator();
      addMessage(botResponse, 'bot');
    } catch (error) {
      removeTypingIndicator();
      addMessage("Sorry, I'm having trouble connecting right now. Please try again later.", 'bot');
      console.error('Error getting response:', error);
    }
  };
}

function injectChatbotCSS() {
  const style = document.createElement('style');
  style.innerHTML = `
    #chatbot-toggle-btn {
      position: fixed;
      top: 32px;
      right: 32px;
      background: #3b82f6;
      color: white;
      border: none;
      border-radius: 50%;
      width: 56px;
      height: 56px;
      font-size: 28px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.3);
      cursor: pointer;
      z-index: 999;
      transition: background 0.3s;
    }
    #chatbot-toggle-btn:hover {
      background: #2563eb;
    }
    #chatbot-overlay {
      position: fixed;
      top: 0;
      right: 0;
      width: 50vw;
      height: 100vh;
      background: #1e3a8a;
      display: flex;
      flex-direction: column;
      justify-content: flex-end;
      z-index: 1000;
      animation: fadeIn 0.3s;
    }
    #chatbot-popup {
      width: 100%;
      height: 100%;
      display: flex;
      flex-direction: column;
      background: #1e293b;
      border-left: 2px solid #60a5fa;
      box-shadow: -8px 0 24px rgba(96,165,250,0.3);
    }
    #chatbot-header {
      background: #2563eb;
      color: white;
      padding: 16px;
      font-size: 18px;
      font-weight: bold;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    #chatbot-close-btn {
      background: none;
      border: none;
      color: white;
      font-size: 24px;
      cursor: pointer;
    }
    #chatbot-messages {
      flex: 1;
      padding: 16px;
      overflow-y: auto;
      background: #1e293b;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
    .chatbot-message {
      max-width: 80%;
    }
    .chatbot-message.user {
      align-self: flex-end;
    }
    .chatbot-message.bot {
      align-self: flex-start;
    }
    .chatbot-bubble {
      background: #3b82f6;
      color: white;
      padding: 10px 14px;
      border-radius: 18px;
      font-size: 15px;
      line-height: 1.4;
    }
    .chatbot-message.user .chatbot-bubble {
      background: #60a5fa;
    }
    .chatbot-bubble.typing {
      display: flex;
      align-items: center;
      justify-content: center;
      min-width: 40px;
      min-height: 24px;
    }
    @keyframes blink {
      0% { opacity: 0.4; }
      50% { opacity: 1; }
      100% { opacity: 0.4; }
    }
    .chatbot-bubble.typing {
      animation: blink 1.5s infinite;
    }
    #chatbot-form {
      display: flex;
      padding: 12px;
      background: #1e293b;
      border-top: 1px solid #60a5fa;
    }
    #chatbot-input {
      flex: 1;
      padding: 10px 14px;
      border-radius: 18px;
      border: 1px solid #60a5fa;
      outline: none;
      background: #0f172a;
      color: white;
    }
    #chatbot-send-btn {
      background: #3b82f6;
      border: none;
      color: white;
      border-radius: 50%;
      width: 46px;
      height: 46px;
      font-size: 20px;
      margin-left: 8px;
      cursor: pointer;
      transition: background 0.2s;
    }
    #chatbot-send-btn:hover {
      background: #2563eb;
    }
    @keyframes fadeIn {
      from {opacity: 0;}
      to {opacity: 1;}
    }
    @media (max-width: 768px) {
      #chatbot-overlay {
        width: 100vw;
        left: 0;
      }
    }
  `;
  document.head.appendChild(style);
}

window.addEventListener('DOMContentLoaded', () => {
  injectChatbotCSS();
  createChatbotUI();
});