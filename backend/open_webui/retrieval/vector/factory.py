from open_webui.retrieval.vector.main import VectorDBBase
from open_webui.retrieval.vector.type import VectorType
from open_webui.config import VECTOR_DB, ENABLE_QDRANT_MULTITENANCY_MODE


class Vector:

    @staticmethod
    def get_vector(vector_type: str) -> VectorDBBase:
        """
        get vector db instance by vector type
        """
        match vector_type:
            case VectorType.DISABLED:
                # Return a no-op client for memory optimization
                return None
            case VectorType.MILVUS:
                from open_webui.retrieval.vector.dbs.milvus import MilvusClient

                return MilvusClient()
            case VectorType.QDRANT:
                if ENABLE_QDRANT_MULTITENANCY_MODE:
                    from open_webui.retrieval.vector.dbs.qdrant_multitenancy import (
                        QdrantClient,
                    )

                    return QdrantClient()
                else:
                    from open_webui.retrieval.vector.dbs.qdrant import QdrantClient

                    return QdrantClient()
            case VectorType.PINECONE:
                from open_webui.retrieval.vector.dbs.pinecone import PineconeClient

                return PineconeClient()
            case VectorType.OPENSEARCH:
                from open_webui.retrieval.vector.dbs.opensearch import OpenSearchClient

                return OpenSearchClient()
            case VectorType.PGVECTOR:
                from open_webui.retrieval.vector.dbs.pgvector import PgvectorClient

                return PgvectorClient()
            case VectorType.ELASTICSEARCH:
                from open_webui.retrieval.vector.dbs.elasticsearch import (
                    ElasticsearchClient,
                )

                return ElasticsearchClient()
            case VectorType.CHROMA:
                from open_webui.retrieval.vector.dbs.chroma import ChromaClient

                return ChromaClient()
            case _:
                raise ValueError(f"Unsupported vector type: {vector_type}")


# Lazy-loaded vector database client
_vector_db_client = None

def get_vector_db_client():
    """Get vector database client with lazy loading"""
    global _vector_db_client
    if _vector_db_client is None:
        _vector_db_client = Vector.get_vector(VECTOR_DB)
    return _vector_db_client

# For backward compatibility - lazy loading with null protection
class VectorDBClientLazy:
    def __getattr__(self, name):
        client = get_vector_db_client()
        if client is None:
            raise RuntimeError("Vector database is disabled (DISABLE_VECTOR_DB=true)")
        return getattr(client, name)
    
    def __call__(self, *args, **kwargs):
        client = get_vector_db_client()
        if client is None:
            raise RuntimeError("Vector database is disabled (DISABLE_VECTOR_DB=true)")
        return client(*args, **kwargs)

VECTOR_DB_CLIENT = VectorDBClientLazy()
