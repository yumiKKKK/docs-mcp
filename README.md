# MCP Document Search

## Requirements

Python 3.10+, Node.js 18+ recommended.

## Run backend

```bash
python -m venv .venv
source .venv\Scripts\activate
python -m pip install -e '.[test]'
```

Run the MCP server :

```bash
python -m server.main
```

Run the HTTP adapter :

```bash
uvicorn server.http_api:app --host 127.0.0.1 --port 8000
```

## Run web UI

```bash
cd web
npm install
npm run dev
```

Open `http://localhost:5173`. 