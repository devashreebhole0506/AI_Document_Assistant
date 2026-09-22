import logging

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException
)

from app.models.schemas import UploadResponse

from app.services.document_service import (
    document_service
)

from app.services.rag_service import (
    rag_service
)


router = APIRouter()

logger = logging.getLogger(__name__)


@router.post(
    "/documents/upload",
    response_model=UploadResponse
)
async def upload_document(
    file: UploadFile = File(...)
):

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="Filename is required."
        )

    extension = ""

    if "." in file.filename:

        extension = (
            "." +
            file.filename.rsplit(".", 1)[1].lower()
        )

    if extension not in (
        document_service.ALLOWED_EXTENSIONS
    ):

        raise HTTPException(
            status_code=400,
            detail="Only PDF and TXT files are supported."
        )

    try:

        content = await file.read()

        file_path = document_service.save_file(
            file.filename,
            content
        )

        chunks = document_service.load_document(
            file_path
        )

        chunk_count = rag_service.add_documents(
            chunks
        )

        logger.info(
            "Document processed: %s | chunks=%s",
            file.filename,
            chunk_count
        )

        return UploadResponse(
            filename=file.filename,
            status="processed",
            chunks=chunk_count
        )

    except Exception as exc:

        logger.exception(
            "Document processing failed"
        )

        raise HTTPException(
            status_code=500,
            detail="Document processing failed."
        ) from exc