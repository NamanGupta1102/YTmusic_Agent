# 🎵 Ultimate YouTube Music AI Agent

A smart, conversational AI agent that curates music, finds hidden gems, and builds playlists for you on **YouTube Music**.

Powered by **Gemini 2.5 Flash Lite** (or **OpenAI**) and a unique "Shopping Cart" conversation engine.

## 🚀 Features
- **Conversational**: Talk to it naturally. "I want some upbeat synthwave."
- **Smart Cart**: It remembers what you like. "Add that to the list."
- **Recommendations**: Finds songs similar to your favorites.
- **Top Songs**: Explore artist discographies.
- **Reliable Auth**: Bypasses YouTube's "Brand Account" limitations using browser headers.

## 🛠️ Setup

### 1. Prerequisites
- Python 3.9+
- A YouTube Music account

### 2. Installation
Clone the repo and install dependencies:
```bash
python -m venv .venv
.venv\Scripts\Activate  # Windows
pip install -r requirements.txt
```

### 3. Authentication (Important!)
Since automated login is blocked by browser security, we use a reliable "Copy as cURL" method.

1.  Open **[YouTube Music](https://music.youtube.com)** in your browser (Chrome/Edge/Brave).
2.  Press `F12` to open Developer Tools.
3.  Go to the **Network** tab.
4.  Refresh the page.
5.  In the "Filter" box, type `browse`.
6.  Right-click the first result (`browse`) -> **Copy** -> **Copy as cURL (bash)**.
    *(Note on Windows: 'Copy as cURL (bash)' is safer than 'cmd').*
7.  Paste the content into the `curl.txt` file in this folder. (Replace any existing text).

The agent will automatically convert this to `browser.json` every time it starts.

### 4. Configure AI
Create a `.env` file (or edit the existing one):

**Option A: Gemini (Free & Fast)**
```ini
GEMINI_API_KEY=your_key_here
GEMINI_MODEL_NAME=gemini-2.5-flash-lite
LLM_name=GEMINI
```

**Option B: OpenAI**
```ini
OPENAI_KEY=your_key_here
OPENAI_MODEL=gpt-4o
LLM_name=OPENAI
```

## ▶️ Usage
### Option A: Web Interface (Recommended)
This launches a modern web app with a visual Shopping Cart.

```bash
# Start the server
.venv\Scripts\python server.py
```
Then open **[http://127.0.0.1:8000](http://127.0.0.1:8000)** in your browser.

- **Status Check**: Look at the "Auth Status" in the sidebar.
- **Update Auth**: Click "Update Auth" and paste your curl command directly in the UI.

### Option B: CLI Mode
Run the agent in your terminal:
```bash
.venv\Scripts\python main.py
```

### Example Conversation:
> **You**: "Who sings 'Blinding Lights'?"
> **Agent**: "That's The Weeknd."
> **You**: "Add it to my cart."
> **Agent**: "Added!"
> **You**: "Find 3 more songs like it."
> **Agent**: "Here are 3 recommendations..."
> **You**: "Add them all and build a playlist called 'Night Drive'."
> **Agent**: "Done! Playlist created."