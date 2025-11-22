# Complete Setup Guide

Follow these commands step-by-step to set up and run the Admin Portal.

## Prerequisites

- Python 3.8+ installed
- Node.js 18+ and npm installed
- MongoDB Atlas account with IP whitelist configured

## Backend Setup

### Step 1: Navigate to Backend Directory
```bash
cd Admin-Portal/Backend
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Create Environment File
Create a `.env` file in `Admin-Portal/Backend/` with:
```env
MONGO_USER=TrueAdmin
MONGO_PASS=TruePassword
MONGO_APPNAME=Chatapi
MONGO_HOST=chatapi.yzflq8h.mongodb.net
BACKEND_PORT=8000
CORS_ORIGINS=http://localhost:3000
```

### Step 5: Run Backend Server
```bash
python main.py
```

Or with auto-reload:
```bash
uvicorn main:app --reload --port 8000
```

**Backend will run on:** `http://localhost:8000`
**API Docs available at:** `http://localhost:8000/docs`

---

## Frontend Setup

### Step 1: Open New Terminal and Navigate to Frontend
```bash
cd Admin-Portal/Frontend
```

### Step 2: Install Dependencies
```bash
npm install
```

### Step 3: (Optional) Create Environment File
Create `.env.local` in `Admin-Portal/Frontend/` with:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Step 4: Run Frontend Development Server
```bash
npm run dev
```

**Frontend will run on:** `http://localhost:3000`

---

## Quick Start (All Commands at Once)

### Backend (Terminal 1)
```bash
cd Admin-Portal/Backend
python -m venv venv
venv\Scripts\activate  # Windows
# OR
source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
python main.py
```

### Frontend (Terminal 2)
```bash
cd Admin-Portal/Frontend
npm install
npm run dev
```

---

## Verify Setup

1. **Backend is running:** Open `http://localhost:8000/docs` - You should see FastAPI Swagger UI
2. **Frontend is running:** Open `http://localhost:3000` - You should see the Admin Portal
3. **Connection:** The frontend should be able to fetch agents from the backend

---

## Troubleshooting

### Backend Issues

**MongoDB Connection Error:**
- Check your IP is whitelisted in MongoDB Atlas
- Verify `.env` file has correct credentials
- Ensure MongoDB cluster is running

**Port Already in Use:**
```bash
# Change BACKEND_PORT in .env file or use different port
uvicorn main:app --reload --port 8001
```

### Frontend Issues

**npm install fails:**
```bash
# Clear cache and retry
npm cache clean --force
npm install
```

**Cannot connect to backend:**
- Ensure backend is running on port 8000
- Check `NEXT_PUBLIC_API_URL` in `.env.local`
- Verify CORS is configured in backend

**Module not found errors:**
```bash
# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

---

## Production Build

### Backend
```bash
cd Admin-Portal/Backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd Admin-Portal/Frontend
npm run build
npm start
```

---

## Stop Servers

- **Backend:** Press `Ctrl+C` in the backend terminal
- **Frontend:** Press `Ctrl+C` in the frontend terminal



