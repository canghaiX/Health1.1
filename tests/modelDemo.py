# app/routes/document_routes.py
import os
import hashlib
import traceback
import aiofiles
import aiofiles.os
from shutil import copyfileobj
from typing import List, Iterable
from fastapi import (
    APIRouter,
    Request,
    UploadFile,
    HTTPException,
    File,
    Form,
    Body,
    Query,
    status,
)
from langchain_core.documents import Document
from langchain_core.runnables import run_in_executor
from langchain_text_splitters import RecursiveCharacterTextSplitter
from functools import lru_cache

from app.config import logger, vector_store, RAG_UPLOAD_DIR, CHUNK_SIZE, CHUNK_OVERLAP
from app.constants import ERROR_MESSAGES
from app.models import (
    StoreDocument,
    QueryRequestBody,
    DocumentResponse,
    QueryMultipleBody,
)
from app.services.vector_store.async_pg_vector import AsyncPgVector
from app.utils.document_loader import get_loader, clean_text, process_documents
from health import is_health_ok
@router.get("/health")
# 执行异步健康监测
async def health_check():
    try:
        if await is_health_ok():
            return {"status": "UP"}
        else:
            logger.error("Health check failed")
            return {"status": "DOWN"}, 503
    except Exception as e:
        logger.error(
            "Error during health check | Error: %s | Traceback: %s",
            str(e),
            traceback.format_exc(),
        )
        return {"status": "DOWN", "error": str(e)}, 503
