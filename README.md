# 🎬 VidNest URL Extractor

A Python + Flask web app that navigates to a target URL, waits 5 seconds, then extracts every URL from the page — anchors, scripts, stylesheets, images, iframes, media sources, lazy-loaded assets, and raw inline URLs.

**Live demo:** deploy to [Render](https://render.com) in under 2 minutes (free tier).

---

## 📁 Project Structure

```
vidnest-extractor/
├── app.py              # Flask backend — fetch, wait, extract
├── requirements.txt    # Python dependencies
├── render.yaml         # Render auto-deploy config
├── Procfile            # Gunicorn start command
├── .gitignore
├── README.md
└── templates/
    └── index.html      # Dark-themed frontend UI
```

---

## 🚀 Deploy to Render (free)

### Step 1 — Push to GitHub

```bash
# In the vidnest-extractor folder:
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/vidnest-extractor.git
git push -u origin main
```

### Step 2 — Create a Render Web Service

1. Go to **[render.com](https://render.com)** → Sign up / Log in
2. Click **"New +"** → **"Web Service"**
3. Click **"Connect a repository"** → select your `vidnest-extractor` repo
4. Fill in the settings:

| Field | Value |
|-------|-------|
| **Name** | `vidnest-url-extractor` *(or anything you like)* |
| **Region** | Closest to you |
| **Branch** | `main` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn app:app --bind 0.0.0.0:$PORT --timeout 60 --workers 1` |
| **Instance Type** | `Free` |

5. Click **"Create Web Service"**

Render will build and deploy automatically. Your app will be live at:
```
https://vidnest-url-extractor.onrender.com
```
*(exact URL shown in your Render dashboard)*

> ⚠️ **Free tier note:** Render free services spin down after 15 minutes of inactivity. The first request after sleep takes ~30s to wake up — totally normal.

---

## 💻 Run Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Start the server
python app.py

# Open browser
open http://localhost:5050
```

---

## ⚙️ How It Works

| Step | What happens |
|------|-------------|
| 1 | Flask receives `GET /fetch` |
| 2 | Requests fetches the target URL with a real browser User-Agent |
| 3 | `time.sleep(5)` — waits 5 seconds for dynamic content |
| 4 | BeautifulSoup + regex sweep extracts all URLs |
| 5 | JSON response sent to the frontend |

**Extracted URL types:** `anchor` · `script` · `link` · `image` · `iframe` · `media-source` · `lazy-src` · `inline`

---

## 🛠 Tech Stack

- **Backend:** Python 3, Flask, Requests, BeautifulSoup4, Gunicorn
- **Frontend:** Vanilla HTML/CSS/JS (no framework, no build step)
- **Hosting:** Render (free tier)
