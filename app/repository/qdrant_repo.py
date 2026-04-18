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
                        "specification": product["specification"]
                    }
                )
            )

        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )