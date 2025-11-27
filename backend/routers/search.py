from fastapi import APIRouter, Query
from services.vector_store import search_similar
from typing import Optional

router = APIRouter(prefix="/api/search", tags=["search"])


@router.get("/")
def search_conversations(
    q: str = Query(..., description="Search query"),
    limit: int = Query(5, description="Number of results"),
    min_score: Optional[float] = Query(None, description="Minimum overall score filter")
):
    """
    Search for similar conversations using semantic search

    Example: /api/search?q=empathetic debt collection&limit=5&min_score=8
    """
    # Build filter
    filter_dict = None
    if min_score is not None:
        filter_dict = {"overall_score": {"$gte": min_score}}

    # Search vector store
    results = search_similar(q, k=limit, filter_dict=filter_dict)

    # Format response
    return {
        "query": q,
        "results": [
            {
                "run_id": int(results["ids"][0][i]),
                "similarity": 1 - results["distances"][0][i],  # Convert distance to similarity
                "transcript": results["documents"][0][i],
                "metadata": results["metadatas"][0][i]
            }
            for i in range(len(results["ids"][0]))
        ]
    }
