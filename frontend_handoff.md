# Backend Handoff & Frontend Briefing

## Project: Agentic YouTube Music Curator
An intelligent, stateful AI agent that helps users discover music and build playlists on YouTube Music.

### Core Architecture
-   **Backend**: Python (3.11+).
-   **LLM Support**: Dual-support for **Gemini 2.5 Flash Lite** (`google-genai`) and **OpenAI** (`openai`). Configurable via `.env`.
-   **State Management**: `agent.state.SessionState` manages a "Shopping Cart" of songs during the conversation.
-   **Authentication**: **Crucial**. Uses `browser.json` generated from a raw `curl` command (`curl.txt`). The agent auto-refreshes this JSON from TXT on startup and before playlist creation.

### Key Files
1.  **`main.py`**: The entry point. Handles the Chat Loop, tool routing (`AVAILABLE_TOOLS`), and LLM initialization.
2.  **`agent/state.py`**: A simple class holding `self.cart`.
3.  **`tools/`**:
    -   `search_tool.py`: `ytmusic.search()`
    -   `recommendation_tool.py`: `ytmusic.get_watch_playlist()` (Radio logic)
    -   `playlist_tool.py`: `ytmusic.create_playlist()` (Requires Auth)
    -   `artist_tool.py`: `ytmusic.get_artist()`
4.  **`scripts/setup_browser_auth.py`**: parser script that converts `curl.txt` -> `browser.json`.

### How to Run (Backend)
```bash
.venv\Scripts\Activate
python main.py
```

### Frontend Requirements (Next Steps)
The user wants to build a Frontend (Web App).
-   **Goal**: Visualize the "Chat" and the live "Shopping Cart".
-   **API Needed**: You will likely need to wrap `main.py` logic into a backend API (FastAPI/Flask) so the frontend can:
    -   Send messages (`POST /chat`).
    -   Get current cart (`GET /cart`).
    -   Trigger auth refresh (`POST /refresh-auth`).
-   **Auth Note**: The frontend needs a way for the user to input their `curl` command string if the backend is running locally, OR a way to guide them to do it manually.

### "Gotchas"
-   **Browser Headers**: The `curl` command expires. The system relies on the user pasting a fresh one into `curl.txt`.
-   **Brand Accounts**: Creating playlists often fails with "400 Bad Request" if the wrong account is used. The current `browser.json` headers method solves this for *most* users.
