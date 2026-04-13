# jabadooble cars generator

A web application for generating printable Dobble-like card games with custom image themes. Design your own themed deck, cartoonize images, and export a print-ready PDF — ready to laminate and play.

## Quick Start

```bash
docker-compose up
```

| Service  | URL                         |
|----------|-----------------------------|
| Frontend | http://localhost:5173        |
| Backend  | http://localhost:8000        |
| API docs | http://localhost:8000/docs   |

## Development

### Backend (FastAPI + Python 3.12)

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
# Tests
pytest tests/ -v
```

### Frontend (SvelteKit + TypeScript)

```bash
cd frontend
npm install
npm run dev
# Tests
npm test
```

## Stack

- **Frontend:** SvelteKit · TypeScript · Material Design 3 Web Components
- **Backend:** FastAPI · Pydantic · Python 3.12
- **PDF export:** ReportLab
- **Cartoonize:** OpenCV
- **Infra:** Docker · docker-compose

## Roadmap

See [project-plan.md](./project-plan.md) for the full phase-by-phase roadmap.
