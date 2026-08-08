---
title: High-Performance Product Catalog Engine
emoji: ⚡
colorFrom: indigo
colorTo: green
sdk: docker
app_port: 7860
pinned: false
---

<div align="center">

# ⚡ High-Performance Product Catalog Engine

### Scalable • Drift-Free • Cursor-Based • Concurrency Aware

A production-style product catalog backend and interactive dashboard designed to demonstrate **stable pagination, indexed database queries, and consistent browsing while data changes in real time**.

[🚀 **Live Demo**](https://kushagra6922-codevector.hf.space) · [💻 **Source Code**](https://github.com/kushagra69yr/codevector)

<br>

![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-D71F00)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-4169E1?logo=postgresql&logoColor=white)
![Pagination](https://img.shields.io/badge/Pagination-Cursor--Based-7C3AED)

</div>

---

## 🎯 The Problem

Traditional **OFFSET-based pagination** becomes inefficient and unreliable as datasets grow and new records are inserted while users are browsing.

A user may see:

- ❌ Duplicate products across pages
- ❌ Products skipped between pages
- ❌ Increasing query cost for deep pages
- ❌ Unstable results when the dataset changes

**This project solves that problem using cursor-based pagination with stable `(created_at, id)` ordering and database indexes.**

---

## 💡 The Core Idea

Instead of asking the database:

> “Skip the first 100,000 rows and give me the next 20.”

we ask:

> “Start immediately after the last product I received.”

### Pagination Flow

```text
┌───────────────┐
│   User opens  │
│    catalog    │
└───────┬───────┘
        │
        ▼
┌──────────────────────┐
│ Request first page   │
│ cursor = none        │
└──────────┬───────────┘
           │
           ▼
┌─────────────────────────────┐
│ Database uses indexed       │
│ (created_at, id) ordering   │
└─────────────┬───────────────┘
              │
              ▼
       ┌──────────────┐
       │  Products    │
       │  1 → 20      │
       └──────┬───────┘
              │
              ▼
┌─────────────────────────────┐
│ Return last item's cursor   │
│ (created_at, id)             │
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│ Next request starts AFTER   │
│ that exact cursor           │
└─────────────┬───────────────┘
              │
              ▼
       ┌──────────────┐
       │  Products    │
       │  21 → 40     │
       └──────────────┘

     New products can be inserted
     without shifting the cursor boundary.
```

---

## 🔥 Why This Project Is Interesting

The project is not just a product listing API. It demonstrates how to design a backend for **large, changing datasets** while keeping pagination stable and queries efficient.

### 1. 🧭 Drift-Free Cursor Pagination

Pagination is anchored to `(created_at, id)` instead of a numeric offset. This keeps the boundary stable even when new products are inserted near the beginning of the catalog.

### 2. ⚡ Indexed Database Seeks

Composite indexes are used to support efficient lookups on the pagination and category fields rather than forcing the database to scan an increasingly large number of rows.

### 3. 🔄 Concurrent Insert Simulation

The dashboard can simulate products being inserted while a user is browsing. This makes the pagination problem visible instead of only describing it theoretically.

### 4. 📊 Performance Testing

The repository includes a test script for comparing pagination approaches and checking behavior during concurrent inserts.

### 5. 🎨 Interactive Dashboard

The frontend includes a modern glassmorphism interface, animated visual effects, catalog browsing, and controls for demonstrating the concurrency scenario.

---

## 📈 Project Scale

| Capability | Implementation |
|---|---|
| Dataset | **200,000+ products** |
| Pagination | **Cursor-based** |
| Stable cursor | **`created_at + id`** |
| Database indexing | **Composite indexes** |
| Concurrency | **Background insert simulation** |
| Backend | **FastAPI + Uvicorn** |
| ORM | **SQLAlchemy** |
| Database | **SQLite / PostgreSQL** |
| Frontend | **HTML + CSS + JavaScript** |

> **Performance figures in this README refer to the project's reported test results. Re-run the included benchmark on your environment to reproduce them.**

---

## 🏗️ System Architecture

```text
                    ┌──────────────────────┐
                    │      Web Browser     │
                    │ Interactive Dashboard │
                    └──────────┬───────────┘
                               │ HTTP
                               ▼
                    ┌──────────────────────┐
                    │      FastAPI         │
                    │  REST API / Routing  │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │     SQLAlchemy       │
                    │    ORM / Queries     │
                    └──────────┬───────────┘
                               │
                     Indexed Queries
                               │
                               ▼
              ┌────────────────────────────────┐
              │        SQLite / PostgreSQL     │
              │                                │
              │  Products + Composite Indexes  │
              └───────────────┬────────────────┘
                              │
                 ┌────────────┴─────────────┐
                 │                          │
                 ▼                          ▼
        ┌─────────────────┐       ┌─────────────────┐
        │ Cursor-based    │       │ Concurrent      │
        │ Pagination      │       │ Inserts         │
        └─────────────────┘       └─────────────────┘
```

---

## 🧠 Technical Deep Dive

### Cursor-Based Pagination

The cursor represents the last item seen by the client. The next query uses that boundary to continue from the correct position.

Conceptually:

```text
Current page:

... → Product A → Product B → Product C
                         ▲
                         │
                    Cursor = C

Next page:

Product C → [start after C] → Product D → Product E → ...
```

The combination of `created_at` and `id` provides a deterministic ordering, including when multiple products share the same timestamp.

### Why `(created_at, id)`?

`created_at` gives the primary chronological ordering, while `id` acts as a deterministic tie-breaker.

That means the database can maintain a predictable order even when timestamps are identical.

---

## 🛠️ Tech Stack

**Backend**
- Python
- FastAPI
- Uvicorn

**Database & Data Access**
- SQLAlchemy
- SQLite
- PostgreSQL
- Composite database indexes

**Frontend**
- HTML5
- CSS3
- Vanilla JavaScript / ES6
- HTML5 Canvas effects

**Engineering Concepts**
- Cursor pagination
- Database indexing
- Query performance
- Concurrent writes
- API design
- Large dataset handling

---

## 🚀 Live Demo

### 👉 [Open the High-Performance Product Catalog Engine](https://kushagra6922-codevector.hf.space)

Try the catalog, explore pagination, and use the concurrency controls to see how the system behaves while products are being inserted.

> **Demo:** `https://kushagra6922-codevector.hf.space`

---

## 💻 Run Locally

### 1. Clone

```bash
git clone https://github.com/kushagra69yr/codevector.git
cd codevector
```

### 2. Create the environment

```bash
python -m venv .venv
```

### 3. Install dependencies

**Windows**

```bash
.\.venv\Scripts\pip install fastapi uvicorn sqlalchemy psycopg2-binary
```

**macOS/Linux**

```bash
./.venv/bin/pip install fastapi uvicorn sqlalchemy psycopg2-binary
```

### 4. Seed 200,000 products

**Windows**

```bash
.\.venv\Scripts\python.exe seed.py
```

**macOS/Linux**

```bash
./.venv/bin/python seed.py
```

### 5. Start the server

```bash
uvicorn main:app --host 127.0.0.1 --port 8000
```

Open:

```text
http://127.0.0.1:8000
```

---

## 🧪 Test Pagination & Concurrency

Run the included benchmark and concurrency test:

**Windows**

```bash
.\.venv\Scripts\python.exe test_pagination.py
```

**macOS/Linux**

```bash
./.venv/bin/python test_pagination.py
```

The test compares pagination behavior and simulates concurrent inserts to verify that the cursor-based approach avoids page overlap/drift.

---

## 📂 Project Structure

```text
codevector/
├── main.py                 # FastAPI application
├── models.py               # Database models
├── database.py             # Database configuration
├── seed.py                 # Large dataset generator
├── test_pagination.py      # Pagination & concurrency tests
├── static/                 # Frontend assets
├── templates/              # HTML templates (if used)
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation
```

---

## 🎓 What I Learned

Building this project helped me understand practical backend engineering concepts beyond basic CRUD APIs:

- Why offset pagination becomes expensive at scale
- How cursor pagination works
- How composite indexes improve database access
- How concurrent writes can affect pagination
- How to design deterministic ordering
- How to benchmark backend/database behavior
- How API and database design work together

---

## 🔮 Future Improvements

- Redis caching for frequently accessed catalog pages
- PostgreSQL query-plan monitoring
- Rate limiting and API authentication
- Docker Compose for local PostgreSQL deployment
- Automated CI/CD performance benchmarks
- Load testing with thousands of concurrent requests

---

## 👨‍💻 Author

**Kushagra Burman**  
B.E. Artificial Intelligence & Machine Learning  
BMS Institute of Technology and Management, Bengaluru

[GitHub](https://github.com/kushagra69yr) · [Portfolio](https://kushagra69yr.github.io/)

---

<div align="center">

### ⭐ If you find the project interesting, consider starring the repository!

**Built to explore what happens when pagination meets scale and concurrency.**

</div>
