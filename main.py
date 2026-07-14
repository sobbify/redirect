import sqlite3
import secrets
from urllib.parse import urlparse
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
import re

app = FastAPI()

# Security: Basic CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_FILE = "redirects.db"
from urllib.parse import urlparse

def check_domain(url: str) -> bool:
    url = url.strip()

    if "://" not in url:
        url = "https://" + url

    parsed = urlparse(url)

    return (
        parsed.scheme in ("http", "https")
        and parsed.netloc
        and "." in parsed.netloc
        and "://" not in parsed.netloc
    )

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS redirects (
            slug TEXT PRIMARY KEY,
            url TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

class RedirectCreate(BaseModel):
    url: str
    slug: Optional[str] = None

@app.get("/", response_class=HTMLResponse)
async def read_index():
    index_path = os.path.join(os.path.dirname(__file__), "index.html")
    if not os.path.exists(index_path):
        return "index.html not found"
    with open(index_path, "r") as f:
        return f.read()

@app.get("/errors/404", response_class=HTMLResponse)
async def read_index():
    index_path = os.path.join(os.path.dirname(__file__), "404.html")
    if not os.path.exists(index_path):
        return "404.html not found."
    with open(index_path, "r", encoding="UTF-8") as f:
        return f.read()

@app.post("/create")
async def create_redirect(data: RedirectCreate):
    url = data.url.strip()

    if "://" not in url:
        url = "https://" + url

    if not check_domain(url):
        raise HTTPException(status_code=400, detail="Invalid URL")
    
    slug = data.slug or secrets.token_urlsafe(6)
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        cursor.execute("INSERT INTO redirects (slug, url) VALUES (?, ?)", (slug, url))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="Slug already exists")
    
    conn.close()
    return {"slug": slug, "url": url}

@app.get("/{slug}")
async def redirect_to_url(slug: str):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT url FROM redirects WHERE slug = ?", (slug,))
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        return RedirectResponse(url="errors/404", status_code=301)
    
    # HTTP 301 is Permanent Redirect
    return RedirectResponse(url=result[0], status_code=301)

@app.get("/check/{slug}")
async def check_slug(slug: str):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT url FROM redirects WHERE slug = ?", (slug,))
    result = cursor.fetchone()
    conn.close()

    return {
        "exists": result is not None
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
