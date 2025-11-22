# Admin Portal Backend

FastAPI backend for managing LLM agents.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file (copy from `.env.example`):
```bash
MONGO_USER=TrueAdmin
MONGO_PASS=TruePassword
MONGO_APPNAME=Chatapi
MONGO_HOST=chatapi.yzflq8h.mongodb.net
BACKEND_PORT=8000
CORS_ORIGINS=http://localhost:3000
```

4. Run the server:
```bash
python main.py
```

Or with uvicorn:
```bash
uvicorn main:app --reload --port 8000
```

5. API will be available at [http://localhost:8000](http://localhost:8000)
6. API documentation at [http://localhost:8000/docs](http://localhost:8000/docs)

## API Endpoints

- `GET /api/agents` - Get all agents
- `GET /api/agents/{agent_id}` - Get agent by ID
- `GET /api/agents/name/{agent_name}` - Get agent by name
- `POST /api/agents` - Create new agent
- `PUT /api/agents/{agent_id}` - Update agent
- `DELETE /api/agents/{agent_id}` - Delete agent



