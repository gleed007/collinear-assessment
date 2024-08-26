from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from auth.routes import router as auth_router
from auth.routes import user_router
from core.database import Base, engine
from dataset.routes import router as dataset_router
from seed import seed_datasets

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(dataset_router)

@app.on_event("startup")
def startup():
    print("Seeding datasets...")
    seed_datasets()
    print("Done seeding datasets!")


@app.get('/')
def health_check():
    return JSONResponse(content={"status": "Running!"})