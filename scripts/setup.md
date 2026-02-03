# YouTube Music Agent Setup

## Prerequisites
- Python 3.9+
- A Google Account (Standard or Brand Account)
- Google Gemini API Key

## 1. Environment Setup
1.  **Clone/Open the Repository**
2.  **Create Virtual Environment:**
    ```bash
    python -m venv .venv
    ```
3.  **Activate:**
    - Windows: `.venv\Scripts\activate`
    - Mac/Linux: `source .venv/bin/activate`
4.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
5.  **Environment Variables:**
    - Create a `.env` file in the root.
    - Add: `GEMINI_API_KEY=your_key_here`

## 2. Authentication (Browser Headers)
Youtube Music API requires authentication to create playlists. We use your browser's cookies.

1.  **Get Headers via Curl:**
    - Open [YouTube Music](https://music.youtube.com) in your browser (Chrome/Firefox/Edge).
    - Open **Developer Tools** (F12) -> **Network** tab.
    - Filter for "browse" (or look for a request to `browse`).
    - Right-click the request -> **Copy** -> **Copy as cURL (bash)**.
    - Paste the content into a new file named `curl.txt` in the project root.

2.  **Generate Credentials:**
    Run the setup script to parse your headers:
    ```bash
    python scripts/setup_browser_auth.py
    ```
    This creates `browser.json`.

3.  **Verify:**
    Run the agent:
    ```bash
    python main.py
    ```
