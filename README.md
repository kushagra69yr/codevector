---
title: High-Performance Product Catalog Engine
emoji: ⚡
colorFrom: indigo
colorTo: green
sdk: docker
app_port: 7860
pinned: false
---

# High-Performance Product Catalog Engine

A premium, high-performance product catalog engine and interactive dashboard built for browsing 200,000+ items with constant-time query speed and zero page overlap/drift under concurrent inserts.

Designed and implemented as a CodeVector take-home task submission.

## 🚀 Key Features

- **Drift-Free Cursor Pagination:** Pins queries to `(created_at, id)` coordinates rather than linear numeric offsets. Concurrent item injections at the top of the feed will not push existing items down, resulting in **zero duplicates** and **zero missed products** during active browsing.
- **Logarithmic Seek Time O(log N):** Uses composite indexes on `(category, created_at DESC, id DESC)` and `(created_at DESC, id DESC)`. Deep-page seeks (e.g. at page depth 100,000) execute in **under 25ms**, avoiding linear database table scans.
- **High-Speed Seeding Engine:** CLI seeding utility populating 200,000 fully structured products with staggered timestamps in **under 7 seconds**.
- **Interactive Concurrency Simulator:** Side-by-side dashboard controls that simulate live database writes in the background so you can observe the boundary-pinning in real-time.
- **Premium Aesthetics:** Modern glassmorphic dark-mode interface with color-shifting background auroras, interactive cursor-reactive constellation physics, and smooth hover micro-animations.

## 🛠️ Tech Stack

- **Backend:** Python (FastAPI + Uvicorn)
- **Database ORM:** SQLAlchemy
- **Supported Databases:** SQLite (default local) and PostgreSQL (Neon/Supabase)
- **Frontend:** Vanilla HTML5, CSS3, & ES6 JavaScript (served statically by FastAPI)
- **Visual Effects:** HTML5 Canvas API

## 💻 How to Setup and Run Locally

1. **Clone or Download** this repository.
2. **Open your terminal** in the project directory.
3. **Initialize the Virtual Environment & Dependencies:**
   ```bash
   python -m venv .venv
   # Windows:
   .\.venv\Scripts\pip install fastapi uvicorn sqlalchemy psycopg2-binary
   # macOS/Linux:
   ./.venv/bin/pip install fastapi uvicorn sqlalchemy psycopg2-binary
   ```
4. **Seed the 200,000 Products Database:**
   ```bash
   # Windows:
   .\.venv\Scripts\python.exe seed.py
   # macOS/Linux:
   ./.venv/bin/python seed.py
   ```
5. **Launch the FastAPI Server:**
   ```bash
   # Windows:
   .\.venv\Scripts\uvicorn.exe main:app --host 127.0.0.1 --port 8000
   # macOS/Linux:
   ./.venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000
   ```
6. **Open in Browser:**
   Go to http://127.0.0.1:8000

## 🧪 Running Concurrency & Performance Tests

We've included a self-contained test script that measures the speed difference between offset and cursor pagination, and simulates concurrent background inserts to verify duplicate prevention:

```bash
# Windows:
.\.venv\Scripts\python.exe test_pagination.py
# macOS/Linux:
./.venv/bin/python test_pagination.py
```
