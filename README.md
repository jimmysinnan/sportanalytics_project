# la soccer Machine — SaaS Analytics Football

Stack: **FastAPI** (Python) + **Next.js 14** (TypeScript)

## Lancer en local

```bash
# Backend (port 8000)
cd backend && python -m venv .venv && .venv/Scripts/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend (port 3000) — dans un autre terminal
cd frontend && npm install && npm run dev
```

Ouvrir : http://localhost:3000

## Docker Compose (full-stack)
```bash
docker-compose up --build
```

## Déploiement
- **Backend** → Railway : `railway up` depuis `/backend`
- **Frontend** → Vercel : `vercel --prod` depuis `/frontend`

## Sources de données
| Source | Usage | Fraîcheur |
|--------|-------|-----------|
| StatsBomb Open Data | Dev, benchmarks, entraînement modèles | Historique |
| FBref (via soccerdata) | Stats saison en cours | Live (~hebdo) |
| Vidéo upload | Analyse contextuelle | Temps réel (à venir) |

## API
Swagger UI disponible sur http://localhost:8000/docs
