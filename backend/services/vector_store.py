import chromadb
from chromadb.utils import embedding_functions

# Initialize ChromaDB client (persistent storage)
client = chromadb.PersistentClient(path="./chroma_db")

# Use default embedding model (all-MiniLM-L6-v2)
embedding_fn = embedding_functions.DefaultEmbeddingFunction()


def init_collection():
    """Get or create the conversations collection"""
    return client.get_or_create_collection(
        name="conversations",
        embedding_function=embedding_fn
    )


def add_conversation(run_id, transcript, metadata=None):
    """
    Add conversation to vector store
    Args:
        run_id: Simulation run ID
        transcript: List of turns [{"agent": "A", "persona": "Marcus", "text": "..."}]
        metadata: Optional dict with persona names, scenario, scores
    """
    collection = init_collection()

    # Format transcript as readable text
    formatted_transcript = "\n".join([
        f"{turn['persona']} ({turn['agent']}): {turn['text']}"
        for turn in transcript
    ])

    # Prepare metadata
    meta = metadata or {}
    meta["run_id"] = run_id

    # Add to ChromaDB (auto-generates embeddings)
    collection.add(
        ids=[str(run_id)],
        documents=[formatted_transcript],
        metadatas=[meta]
    )

    print(f"Added conversation run_id={run_id} to vector store")


def search_similar(query, k=5, filter_dict=None):
    """
    Search for similar conversations
    Args:
        query: Search query (e.g., "empathetic debt collection")
        k: Number of results to return
        filter_dict: Optional metadata filter (e.g., {"overall_score": {"$gt": 8}})
    Returns:
        Results with documents, metadatas, distances
    """
    collection = init_collection()

    # Query ChromaDB
    results = collection.query(
        query_texts=[query],
        n_results=k,
        where=filter_dict
    )

    return results


def get_conversation_by_id(run_id):
    """Get specific conversation from vector store"""
    collection = init_collection()

    try:
        results = collection.get(ids=[str(run_id)])
        return results
    except Exception as e:
        print(f"Error retrieving conversation {run_id}: {e}")
        return None
