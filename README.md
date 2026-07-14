# redirect

A bare-minimum, public redirecter service.

## Features
- **Public Access:** No authentication required to create redirects.
- **Permanent Redirects:** Uses HTTP 301 status codes.
- **SQLite Persistence:** Redirects are saved in a local database file.
- **Bare Minimum UI:** Pure HTML/CSS/JS frontend.

## Local Setup

1. **Install Dependencies**
   ```bash
   pip install fastapi uvicorn
   ```

2. **Run the Application**
   ```bash
   python main.py
   ```

3. **Usage**
   - Open `http://localhost:8000` in your browser.
   - Enter a URL and an optional slug to create a permanent redirect.
   - The database (`redirects.db`) will be created automatically in the same folder.
