# LLM Agents Admin Portal

A full-stack admin portal for managing LLM agents with FastAPI backend and Next.js frontend.

## Project Structure

```
Admin-Portal/
├── Backend/          # FastAPI backend
│   ├── main.py       # Main API application
│   ├── models.py     # Pydantic models
│   ├── database.py   # MongoDB connection
│   └── requirements.txt
└── Frontend/          # Next.js frontend
    ├── app/          # Next.js app directory
    ├── components/   # React components
    ├── services/     # API service layer
    └── types/        # TypeScript types
```

## Quick Start

### Backend Setup

1. Navigate to the backend directory:
```bash
cd Admin-Portal/Backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file:
```env
MONGO_USER=TrueAdmin
MONGO_PASS=TruePassword
MONGO_APPNAME=Chatapi
MONGO_HOST=chatapi.yzflq8h.mongodb.net
BACKEND_PORT=8000
CORS_ORIGINS=http://localhost:3000
```

5. Run the backend:
```bash
python main.py
```

The API will be available at `http://localhost:8000`
API documentation at `http://localhost:8000/docs`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd Admin-Portal/Frontend
```

2. Install dependencies:
```bash
npm install
```

3. (Optional) Create a `.env.local` file:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

4. Run the frontend:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Features

- ✅ View all agents
- ✅ Create new agents
- ✅ Edit existing agents
- ✅ Delete agents
- ✅ Responsive UI with Tailwind CSS
- ✅ Real-time error handling and notifications
- ✅ JSON validation for example queries

## Agent Structure

Each agent follows this structure (matching `mongo.py`):

- `name`: String - Unique agent name
- `api_key`: String - API key for the LLM provider
- `system_prompt`: String - System instructions for the agent
- `endpoint`: String - API endpoint URL
- `endpoint_info`: String - Description of the endpoint
- `example_query`: JSON object - Example API query
- `test_scenarios`: String - Test scenarios and expected responses
- `created_at`: DateTime - Creation timestamp

## API Endpoints

- `GET /api/agents` - Get all agents
- `GET /api/agents/{agent_id}` - Get agent by ID
- `GET /api/agents/name/{agent_name}` - Get agent by name
- `POST /api/agents` - Create new agent
- `PUT /api/agents/{agent_id}` - Update agent
- `DELETE /api/agents/{agent_id}` - Delete agent

## Development

### Backend Development
- Uses FastAPI with automatic API documentation
- MongoDB connection with proper error handling
- CORS configured for frontend communication

### Frontend Development
- Next.js 14 with App Router
- TypeScript for type safety
- Tailwind CSS for styling
- React Hot Toast for notifications
- Axios for API calls

## Notes

- Make sure MongoDB Atlas IP whitelist includes your IP address
- Backend and frontend should run simultaneously for full functionality
- All agent data is stored in MongoDB `LLM_Agents.Agent_info` collection



