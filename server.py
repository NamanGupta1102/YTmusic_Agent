import os
import logging
from typing import Optional
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Import the Agent from main.py
# (We need to make sure main.py is importable without running main())
from main import get_agent, session
from scripts.setup_browser_auth import parse_curl_and_save

# Load env
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("server")

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Enable CORS (just in case)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Agent once
# NOTE: In a real multi-user app, we'd need a manager to create agents per session.
# For this single-user local tool, a global agent instance is acceptable.
try:
    agent = get_agent()
    logger.info("Agent initialized successfully.")
except Exception as e:
    logger.error(f"Failed to init agent: {e}")
    agent = None

# --- DATA MODELS ---
class ChatRequest(BaseModel):
    message: str

class AuthRequest(BaseModel):
    curl_command: str

class ChatResponse(BaseModel):
    agent_response: str
    cart: list

# --- ROUTES ---

@app.get("/")
async def get_index():
    return FileResponse("static/index.html")

@app.post("/api/chat")
async def chat(request: ChatRequest):
    if not agent:
        raise HTTPException(status_code=500, detail="Agent not initialized. Check server logs.")
    
    try:
        response_text = agent.send_message(request.message)
        return {
            "agent_response": response_text,
            "cart": session.get_cart()
        }
    except Exception as e:
        logger.error(f"Chat Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/cart")
async def get_cart():
    print("GETTING CART")
    return {"cart": session.get_cart()}

@app.post("/api/auth")
async def update_auth(request: AuthRequest):
    """
    Updates the curl.txt file and runs the auth parser.
    """
    curl_cmd = request.curl_command.strip()
    if not curl_cmd:
        raise HTTPException(status_code=400, detail="Empty Command")

    try:
        # Write to curl.txt
        with open("curl.txt", "w", encoding="utf-8") as f:
            f.write(curl_cmd)
        
        # Run parser
        parse_curl_and_save()
        return {"status": "success", "message": "Auth updated! You can now use Playlist features."}
    except Exception as e:
        logger.error(f"Auth Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
