import os
from app.config.env_config import settings
from app.config.log_config import logger
from app.constants.app_constants import VECTOR_DB


from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient, models
from qdrant_client.models import PointStruct

class QdrantRepository:
    """Qdrant vector database configuration"""

    def __init__(self, embeddings, collection_name, host = settings.QDRANT_HOST, port=settings.QDRANT_PORT, path = None):
        """Initialize the repo
        Args:
        embeddings: embedding model for vectorization
        collection_name: name of the collection
        host: Qdrant service name in docker-compose
        port: Qdrant port (default 6333)
        path: If using local storage instead of server (optional)
        """
        self.embeddings = embeddings
        self.collection_name = collection_name

        if path:
            self.client = QdrantClient(path=path)
            logger.info(f"Qdrant initialized locally at {path}")
        else:
            self.client = QdrantClient(host=host, port=port)
            logger.info(f"Qdrant connecting to {host}:{port}")

        if not self.client.collection_exists(self.collection_name):
            self.client.create_collection(
                collection_name= self.collection_name,
                vectors_config={
                    "dense": models.VectorParams(
                        size=self.client.get_embedding_size(VECTOR_DB.EMBEDDING_MODEL.value),
                        distance=models.Distance.COSINE
                    )
                },
                sparse_vectors_config= {
                    "sparse": models.SparseVectorParams()
                }
            )
            logger.info(f"Hybrid collection '{self.collection_name}' created.")

        self.vector_store = QdrantVectorStore(
            client=self.client,
            collection_name=self.collection_name,
            embedding=self.embeddings,
            vector_name="dense"
        )

    def build_text(self, product):
        specs_text = " ".join([f"{k}: {v}" for k, v in product["specification"].items()])
        
        return f"""
        {product['name']}
        {product['about']}
        {product['description']}
        {specs_text}
        """

    def add_documents(self, documents):
        """Add the document using the add_documents method"""
        logger.info(f"Adding {len(documents)} docs with Qdrant Hybrid Search...")

        if not documents:
            return
        
        source_name = documents[0].get("source")

        if source_name and self.source_exists(source_name):
            logger.warning(f"Source '{source_name}' already exists. Skipping ingestion.")
            return

        points = []

        for i, product in enumerate(documents):
            text = self.build_text(product)

            points.append(
                PointStruct(
                    id=product["id"],
                    vector={
                        "dense": models.Document(
                            text=text,
                            model=VECTOR_DB.EMBEDDING_MODEL.value
                        ),
                        "sparse": models.Document(
                            text=text,
                            model=VECTOR_DB.SPARSE_MODEL.value
                        )
                    },
                    payload={
                        "name": product["name"],
                        "price": product["price"],
                        "page": product["page"],
                        "about": product["about"],
                        "description": product["description"],
                        "specification": product["specification"],
                        "source": product['source']
                    }
                )
            )

        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

    def source_exists(self, source_name: str) -> bool:
        """Efficiently queries Qdrant metadata using the Scroll API."""
        try:
            results, _ = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="source",
                        match=models.MatchValue(value=source_name),
                    )
                ]
                ),
                limit=1
            )
            return len(results) > 0

        except Exception as e:
            logger.error(f"Error checking Qdrant for file: {e}")
            return False  
        
    def search(self, query, k=5):
        """Performs Hybrid Search using Reciprocal Rank Fusion (RRF)"""
        results = self.client.query_points(
            collection_name= self.collection_name,
            query=models.FusionQuery(
                fusion=models.Fusion.RRF
            ),
            prefetch=[
                models.Prefetch(
                query=models.Document(text=query, model=VECTOR_DB.EMBEDDING_MODEL.value),
                using="dense",
                ),
                models.Prefetch(
                query=models.Document(text=query, model=VECTOR_DB.SPARSE_MODEL.value),
                using="sparse",
                ),
            ],
            query_filter=None, 
            limit=k
        ).points

        formatted_results = []

        for res in results:
            payload = res.payload or {}

            formatted_results.append({
                "id": res.id,
                "score": res.score,
                "name": payload.get("name"),
                "price": payload.get("price"),
                "about": payload.get("about"),
                "description": payload.get("description"),
                "specification": payload.get("specification"),
            })

        return formatted_results