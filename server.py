"""KPSS Quest FastAPI Backend - offline-first exam prep app."""
from fastapi import FastAPI, APIRouter, Header, HTTPException, Body
from fastapi.responses import StreamingResponse, RedirectResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import uuid
import httpx
import urllib.parse
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone, timedelta

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

from seed_data import QUESTIONS, FLASHCARDS, VIDEOS

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY', '')

app = FastAPI(title="KPSS Quest API")
api_router = APIRouter(prefix="/api")

# ---------------- Models ----------------
class SessionRequest(BaseModel):
    session_id: str

class User(BaseModel):
    user_id: str
    email: str
    name: str
    picture: Optional[str] = None
    exam_target_date: Optional[str] = None
    xp_points: int = 0
    streak_count: int = 0
    current_lives: int = 3
    language: str = "tr"
    created_at: str

class Question(BaseModel):
    id: str
    subject: str
    topic: str
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_option: str
    difficulty: int
    is_frequently_asked: bool

class Flashcard(BaseModel):
    id: str
    subject: str
    front_text: str
    back_text: str

class Video(BaseModel):
    id: str
    title: str
    video_url: str
    subject: str

class ProgressUpdate(BaseModel):
    subject: str
    topic: str
    correct: int = 0
    wrong: int = 0
    xp_gained: int = 0

class OnboardingUpdate(BaseModel):
    exam_target_date: str

class LanguageUpdate(BaseModel):
    language: str

class SyncPayload(BaseModel):
    progress_updates: List[ProgressUpdate] = []
    xp_gained: int = 0
    streak_count: Optional[int] = None
    lives: Optional[int] = None

class ExplainRequest(BaseModel):
    question: str
    correct_answer: str
    user_answer: str
    language: str = "tr"

# ---------------- Helpers ----------------
async def get_user_from_token(authorization: Optional[str]) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="missing_authorization")
    token = authorization.split(" ", 1)[1].strip()
    session = await db.user_sessions.find_one({"session_token": token}, {"_id": 0})
    if not session:
        raise HTTPException(status_code=401, detail="invalid_session")
    exp = session.get("expires_at")
    if isinstance(exp, datetime):
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=timezone.utc)
        if exp < datetime.now(timezone.utc):
            raise HTTPException(status_code=401, detail="session_expired")
    user = await db.users.find_one({"user_id": session["user_id"]}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=401, detail="user_not_found")
    return user

# ---------------- DOĞRUDAN GOOGLE AUTH KODLARI ----------------
@api_router.get("/auth/login")
async def auth_login(redirect: str):
    client_id = os.environ.get("GOOGLE_CLIENT_ID")
    redirect_uri = f"{os.environ.get('EXPO_PUBLIC_BACKEND_URL')}/api/auth/callback"
    state = urllib.parse.quote(redirect)
    
    url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"response_type=code&client_id={client_id}&"
        f"redirect_uri={redirect_uri}&"
        f"scope=openid%20email%20profile&state={state}"
    )
    return RedirectResponse(url=url)

@api_router.get("/auth/callback")
async def auth_callback(code: str, state: str):
    client_id = os.environ.get("GOOGLE_CLIENT_ID")
    client_secret = os.environ.get("GOOGLE_CLIENT_SECRET")
    redirect_uri = f"{os.environ.get('EXPO_PUBLIC_BACKEND_URL')}/api/auth/callback"
    
    async with httpx.AsyncClient() as hc:
        token_res = await hc.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": client_id,
                "client_secret": client_secret,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": redirect_uri
            }
        )
        token_data = token_res.json()
        access_token = token_data.get("access_token")
        
        # İŞTE BURAYI DEĞİŞTİRDİK - ARTIK BİZE GERÇEK HATAYI SÖYLEYECEK!
        if not access_token:
            raise HTTPException(status_code=400, detail=token_data)
        
        user_res = await hc.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        user_info = user_res.json()
        
    email = user_info.get("email")
    name = user_info.get("name") or email
    picture = user_info.get("picture")
    
    if not email:
        raise HTTPException(status_code=400, detail="no_email_found")
        
    session_token = f"sess_{uuid.uuid4().hex}"
    existing = await db.users.find_one({"email": email}, {"_id": 0})
    now = datetime.now(timezone.utc)
    
    if existing:
        user_id = existing["user_id"]
        await db.users.update_one(
            {"user_id": user_id},
            {"$set": {"name": name, "picture": picture}},
        )
    else:
        user_id = f"user_{uuid.uuid4().hex[:12]}"
        user_doc = {
            "user_id": user_id,
            "email": email,
            "name": name,
            "picture": picture,
            "exam_target_date": None,
            "xp_points": 0,
            "streak_count": 0,
            "current_lives": 3,
            "language": "tr",
            "created_at": now.isoformat(),
        }
        await db.users.insert_one(user_doc)

    await db.user_sessions.insert_one({
        "session_token": session_token,
        "user_id": user_id,
        "created_at": now,
        "expires_at": now + timedelta(days=7),
    })
    
    app_redirect = urllib.parse.unquote(state)
    sep = "&" if "?" in app_redirect else "?"
    final_url = f"{app_redirect}{sep}session_id={session_token}"
    return RedirectResponse(url=final_url)

@api_router.post("/auth/session")
async def verify_session(payload: SessionRequest):
    session_token = payload.session_id
    session = await db.user_sessions.find_one({"session_token": session_token}, {"_id": 0})
    if not session:
        raise HTTPException(status_code=401, detail="invalid_session")
    user = await db.users.find_one({"user_id": session["user_id"]}, {"_id": 0})
    return {"session_token": session_token, "user": user}

@api_router.get("/auth/me")
async def me(authorization: Optional[str] = Header(default=None)):
    user = await get_user_from_token(authorization)
    return {"user": user}

@api_router.post("/auth/logout")
async def logout(authorization: Optional[str] = Header(default=None)):
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ", 1)[1].strip()
        await db.user_sessions.delete_one({"session_token": token})
    return {"ok": True}

# ---------------- Profile ----------------
@api_router.post("/profile/onboarding")
async def set_onboarding(payload: OnboardingUpdate, authorization: Optional[str] = Header(default=None)):
    user = await get_user_from_token(authorization)
    await db.users.update_one(
        {"user_id": user["user_id"]},
        {"$set": {"exam_target_date": payload.exam_target_date}},
    )
    user["exam_target_date"] = payload.exam_target_date
    return {"user": user}

@api_router.post("/profile/language")
async def set_language(payload: LanguageUpdate, authorization: Optional[str] = Header(default=None)):
    user = await get_user_from_token(authorization)
    lang = payload.language if payload.language in ("tr", "en") else "tr"
    await db.users.update_one({"user_id": user["user_id"]}, {"$set": {"language": lang}})
    return {"language": lang}

# ---------------- Content ----------------
@api_router.get("/questions")
async def get_questions(subject: Optional[str] = None):
    q = {}
    if subject:
        q["subject"] = subject
    items = await db.questions.find(q, {"_id": 0}).to_list(1000)
    return {"items": items}

@api_router.get("/flashcards")
async def get_flashcards(subject: Optional[str] = None):
    q = {}
    if subject:
        q["subject"] = subject
    items = await db.flashcards.find(q, {"_id": 0}).to_list(1000)
    return {"items": items}

@api_router.get("/videos")
async def get_videos(subject: Optional[str] = None):
    q = {}
    if subject:
        q["subject"] = subject
    items = await db.videos.find(q, {"_id": 0}).to_list(1000)
    return {"items": items}

# ---------------- Progress & Sync ----------------
@api_router.post("/sync")
async def sync(payload: SyncPayload, authorization: Optional[str] = Header(default=None)):
    user = await get_user_from_token(authorization)
    uid = user["user_id"]

    for pu in payload.progress_updates:
        await db.user_progress.update_one(
            {"user_id": uid, "subject": pu.subject, "topic": pu.topic},
            {"$inc": {"correct_answers": pu.correct, "wrong_answers": pu.wrong}},
            upsert=True,
        )

    update = {}
    if payload.xp_gained:
        update["$inc"] = {"xp_points": payload.xp_gained}
    setters = {}
    if payload.streak_count is not None:
        setters["streak_count"] = payload.streak_count
    if payload.lives is not None:
        setters["current_lives"] = payload.lives
    if setters:
        update["$set"] = setters
    if update:
        await db.users.update_one({"user_id": uid}, update)

    updated_user = await db.users.find_one({"user_id": uid}, {"_id": 0})
    progress = await db.user_progress.find({"user_id": uid}, {"_id": 0}).to_list(1000)
    return {"user": updated_user, "progress": progress}

@api_router.get("/progress")
async def get_progress(authorization: Optional[str] = Header(default=None)):
    user = await get_user_from_token(authorization)
    progress = await db.user_progress.find({"user_id": user["user_id"]}, {"_id": 0}).to_list(1000)
    return {"progress": progress}

# ---------------- Leaderboard ----------------
@api_router.get("/leaderboard")
async def leaderboard(authorization: Optional[str] = Header(default=None)):
    user = await get_user_from_token(authorization)
    top = await db.users.find({}, {"_id": 0, "user_id": 1, "name": 1, "picture": 1, "xp_points": 1, "streak_count": 1})\
        .sort("xp_points", -1).limit(50).to_list(50)
    return {"leaderboard": top, "current_user_id": user["user_id"]}

# ---------------- AI Explain ----------------
@api_router.post("/ai/explain")
async def explain(payload: ExplainRequest, authorization: Optional[str] = Header(default=None)):
    await get_user_from_token(authorization)
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"llm_lib_missing: {e}")

    lang_instr = (
        "Türkçe yanıt ver. Kısa (maks 4 cümle), açıklayıcı ve öğrenci dostu ol."
        if payload.language == "tr"
        else "Reply in English. Keep it concise (max 4 sentences), clear, and student-friendly."
    )
    sys_msg = f"You are a KPSS exam tutor for Turkish students. {lang_instr}"

    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=f"explain_{uuid.uuid4().hex}",
        system_message=sys_msg,
    ).with_model("gemini", "gemini-3-flash-preview")

    prompt_tr = (
        f"Soru: {payload.question}\n"
        f"Doğru cevap: {payload.correct_answer}\n"
        f"Kullanıcının cevabı: {payload.user_answer}\n"
        f"Doğru cevabın neden doğru olduğunu ve kullanıcının hatasını kısaca açıkla."
    )
    prompt_en = (
        f"Question: {payload.question}\n"
        f"Correct answer: {payload.correct_answer}\n"
        f"User's answer: {payload.user_answer}\n"
        f"Explain briefly why the correct answer is right and what the user got wrong."
    )
    user_msg = UserMessage(text=prompt_tr if payload.language == "tr" else prompt_en)

    try:
        response = await chat.send_message(user_msg)
        text = response if isinstance(response, str) else str(response)
        return {"explanation": text}
    except Exception as e:
        logging.exception("ai explain failed")
        raise HTTPException(status_code=502, detail=f"ai_error: {e}")

# ---------------- Health ----------------
@api_router.get("/")
async def root():
    return {"message": "KPSS Quest API", "ok": True}

# ---------------- Seed (GÜNCELLENDİ: ESKİLERİ SİLİP YENİLERİ EKLER) ----------------
async def seed_content():
    # 1. Eski veritabanını tamamen temizliyoruz (Yeni verilerle çakışmasın diye)
    await db.questions.delete_many({})
    await db.flashcards.delete_many({})
    await db.videos.delete_many({})
    
    # 2. Yeni ve güncel verileri tertemiz bir şekilde ekliyoruz
    docs_q = [{**q, "id": str(uuid.uuid4())} for q in QUESTIONS]
    if docs_q:
        await db.questions.insert_many(docs_q)
        logging.info("YENI: %d soru eklendi", len(docs_q))
    
    docs_f = [{**f, "id": str(uuid.uuid4())} for f in FLASHCARDS]
    if docs_f:
        await db.flashcards.insert_many(docs_f)
        logging.info("YENI: %d flashcard eklendi", len(docs_f))
    
    docs_v = [{**v, "id": str(uuid.uuid4())} for v in VIDEOS]
    if docs_v:
        await db.videos.insert_many(docs_v)
        logging.info("YENI: %d video eklendi", len(docs_v))

@app.on_event("startup")
async def startup_event():
    await db.users.create_index("email", unique=True)
    await db.users.create_index("user_id", unique=True)
    await db.user_sessions.create_index("session_token", unique=True)
    await db.user_sessions.create_index("user_id")
    await db.user_sessions.create_index("expires_at", expireAfterSeconds=0)
    await db.user_progress.create_index([("user_id", 1), ("subject", 1), ("topic", 1)])
    await seed_content()

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
