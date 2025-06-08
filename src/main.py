from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.responses import Response
import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="4-Player Chess",
    description="Real-time multiplayer chess with Chaturaji and Enochian variants",
    version="1.0.0"
)

# Static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/lobby", response_class=HTMLResponse) 
async def lobby(request: Request):
    return templates.TemplateResponse("lobby.html", {"request": request})

@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})

@app.get("/create", response_class=HTMLResponse)
async def create_game(request: Request):
    return templates.TemplateResponse("create.html", {"request": request})

@app.get("/game/quick", response_class=HTMLResponse)
async def quick_game(request: Request):
    # For now, redirect to a sample game
    return templates.TemplateResponse("game.html", {
        "request": request, 
        "game_id": "quick-match",
        "variant": "chaturaji"
    })

@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "connected", "redis": "connected"}

# Add favicon to stop 404 errors
@app.get("/favicon.ico")
async def favicon():
    return Response(status_code=204)  # No content

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
