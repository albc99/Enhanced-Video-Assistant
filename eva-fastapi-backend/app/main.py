from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth,eva,azure_blob,projects
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()

# Set up CORS middleware configurationorigins = [
origins = [
    "http://localhost:5173",
    "http://localhost",
    "http://localhost:4173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Replace with your frontend's local address
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# routers from the routers directory
app.include_router(auth.router)
app.include_router(eva.router)
app.include_router(projects.router)
app.include_router(azure_blob.router)

# Initialize session middleware
app.add_middleware(SessionMiddleware, secret_key="EVAisAwesome")




@app.get("/")
async def get_home():
    return {"Hello World": "EVA FastAPI Backend"}



