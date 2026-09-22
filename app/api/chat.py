import logging

from fastapi import APIRouter, HTTPException

from app.models.schemas import (
    ChatRequest,
    ChatResponse,
    Source
)

from app.services.llm_service import (
    llm_service
)

from app.services.memory_service import (
    memory_service
)

from app.services.rag_service import (
    rag_service
)


router = APIRouter()

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """
You are an AI Document Assistant.

Your task is to answer user questions using
the provided document context.

Rules:

1. Use the document context when answering.
2. Do not invent information.
3. If the answer is not available in the
   provided document context, clearly say that
   the information was not found in the
   uploaded documents.
4. Give clear and concise answers.
5. Use conversation history when useful.
"""


@router.post(
    "/chat",
    response_model=ChatResponse
)
async def chat(
    request: ChatRequest
):

    try:

        history = memory_service.get_history(
            request.session_id
        )

        retrieved_documents = (
            rag_service.retrieve(
                request.message,
                k=4
            )
        )

        context_parts = []
        sources = []

        for document in retrieved_documents:

            text = document.page_content

            metadata = document.metadata

            context_parts.append(text)

            source_name = metadata.get(
                "source",
                "Unknown document"
            )

            page_number = metadata.get(
                "page"
            )

            if page_number is not None:

                page_number = (
                    int(page_number) + 1
                )

            sources.append(
                Source(
                    document=source_name,
                    page=page_number
                )
            )

        context = "\n\n".join(
            context_parts
        )

        user_prompt = f"""
Document Context:

{context}

User Question:

{request.message}

Answer the question using the
document context above.
"""

        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }
        ]

        messages.extend(history)

        messages.append(
            {
                "role": "user",
                "content": user_prompt
            }
        )

        answer = await llm_service.generate_response(
            messages
        )

        memory_service.add_message(
            request.session_id,
            "user",
            request.message
        )

        memory_service.add_message(
            request.session_id,
            "assistant",
            answer
        )

        unique_sources = []

        seen = set()

        for source in sources:

            key = (
                source.document,
                source.page
            )

            if key not in seen:

                seen.add(key)

                unique_sources.append(
                    source
                )

        return ChatResponse(
            session_id=request.session_id,
            response=answer,
            sources=unique_sources
        )

    except Exception as exc:

        logger.exception(
            "Chat processing failed"
        )

        raise HTTPException(
            status_code=503,
            detail="Unable to process chat request."
        ) from exc