from collections import defaultdict
from fastapi import FastAPI
from fastapi import status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from src.facets.router import router as facet_router
from src.categories_admin.router import router as category_router
from src.facet_types.router import router as facet_type_router
from src.variaton_themes.router import router as variation_theme_router
from src.products_admin.router import router as product_admin_router
from src.synonyms.router import router as synonym_router

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
app.include_router(variation_theme_router)
app.include_router(product_admin_router)
app.include_router(synonym_router)


@app.exception_handler(RequestValidationError)
async def custom_form_validation_error(request, exc):
    reformatted_message = defaultdict(list)
    for pydantic_error in exc.errors():
        loc, msg = pydantic_error["loc"], pydantic_error["msg"].capitalize()
        filtered_loc = loc[1:] if loc[0] in ("body", "query", "path") else loc
        field_string = ".".join(map(str, filtered_loc))  # nested fields with dot-notation
        reformatted_message[field_string].append(msg)

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=jsonable_encoder(
            {"detail": "Invalid request", "errors": reformatted_message, "base_errors": True}
        ),
    )

@app.get("/ping")
async def ping():
    return {"response": "pong"}
