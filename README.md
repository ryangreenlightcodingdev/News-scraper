# 🧠 News Intelligence Dashboard

A full-stack web app that aggregates tech, Hacker News, political, and medical research (peptides, longevity, brain health) into a single dashboard.

## 🚀 Features

* 🔥 Aggregates multiple news sources:

  * Tech news
  * Hacker News
  * Political news
  * Medical research (peptides, anti-aging, longevity, brain health)

* 🧬 Research integration via PubMed (abstracts + summaries)

* 📊 Clean dashboard UI with categories

* ⚡ FastAPI backend + React frontend

* 🔄 Auto-refreshing data pipeline

---

## 🛠️ Tech Stack

* **Backend:** Python, FastAPI
* **Frontend:** React, Vite
* **Database:** SQLite
* **Other:** Web scraping + APIs

---

## 📦 Project Structure

```
app-jobs/
├── backend/
│   ├── app/
│   ├── requirements.txt
│   └── .env (not included)
├── frontend/
│   ├── src/
│   └── package.json
└── README.md
```

---

## ⚙️ Getting Started

### 1. Clone the repo

```
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO
```

---

### 2. Backend setup

```
cd backend
python -m venv .venv
source .venv/Scripts/activate   # Windows (Git Bash)
# OR
.venv\Scripts\activate          # PowerShell

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

---

### 3. Run backend

```
uvicorn app.main:app --reload
```

Backend will run at:

```
http://127.0.0.1:8000
```

---

### 4. Frontend setup

Open a new terminal:

```
cd frontend
npm install
npm run dev
```

Frontend will run at:

```
http://127.0.0.1:5173
```

---

## 🔐 Environment Variables

Create a `.env` file inside `backend/`:

```
# Example
API_KEY=your_api_key_here
```

⚠️ Never commit your `.env` file.

---

## 💡 Future Improvements

* 🤖 AI-powered summaries
* 📬 Email / daily digest
* 👤 User personalization
* 📈 Trending topics detection
* ☁️ Deployment (Vercel + cloud backend)

---

## 📸 Screenshot

*Add a screenshot of your dashboard here*

---

## 🧭 Vision

This project aims to evolve into a **personal intelligence dashboard**—helping users stay on top of technology, global events, and cutting-edge health research in one place.

---

## 📄 License

MIT
