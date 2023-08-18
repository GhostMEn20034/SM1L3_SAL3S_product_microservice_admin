from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.facets.router import router as facet_router
from src.categories.router import router as category_router
from src.facet_types.router import router as facet_type_router

origins = [
    "http://localhost:3001",
]


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(facet_router)
app.include_router(category_router)
app.include_router(facet_type_router)


@app.get("/ping")
async def ping():
    return {"response": "pong"}
