from collections import defaultdict
from typing import Optional

from fastapi import FastAPI
from fastapi import status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from src.apps.facets.router import router as facet_router
from src.apps.categories.router import router as category_router
from src.apps.facet_types.router import router as facet_type_router
from src.apps.variaton_themes.router import router as variation_theme_router
from src.apps.products.router import router as product_admin_router
from src.apps.synonyms.router import router as synonym_router
from src.apps.events.router import router as event_admin_router
from src.apps.deals.router import router as deal_admin_router
from src.apps.search_terms.router import router as search_terms_admin_router
from src.core.message_broker.async_consumer import AsyncConsumer

from src.config import settings
from src.core.queue_listener_initializers import initialize_order_processing_listener

origins = settings.ALLOWED_ORIGINS

app = FastAPI()

# Will be initialized on app startup
order_processing_listener: Optional[AsyncConsumer] = None

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
app.include_router(event_admin_router)
app.include_router(deal_admin_router)
app.include_router(search_terms_admin_router)


@app.exception_handler(RequestValidationError)
async def custom_form_validation_error(_, exc):
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

@app.on_event("startup")
async def initialize_app():
    global order_processing_listener
    order_processing_listener = await initialize_order_processing_listener()  # Initialize and start the listener

@app.on_event("shutdown")
async def shutdown_event():
    if order_processing_listener:
        await order_processing_listener.close()


@app.get("/ping")
async def ping():
    return {"response": "pong"}
