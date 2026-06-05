from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.competitions import router as competitions_router
from routers.players import router as players_router
from routers.match import router as match_router
from routers.tactical import router as tactical_router
from routers.pdf import router as pdf_router
from routers.fbref import router as fbref_router
from routers.social.profiles import router as social_profiles_router
from routers.social.matches import router as social_matches_router
from routers.social.votes import router as social_votes_router

app = FastAPI(title="la soccer Machine API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(competitions_router)
app.include_router(players_router)
app.include_router(match_router)
app.include_router(tactical_router)
app.include_router(pdf_router)
app.include_router(fbref_router)
app.include_router(social_profiles_router)
app.include_router(social_matches_router)
app.include_router(social_votes_router)

@app.get("/health")
def health():
    return {"status": "ok"}
