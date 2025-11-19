import numpy as np
from numpy.typing import NDArray
from typing import Any
import llm

DENSE_MODELS = ["all-MiniLM-L6-v2", "Qodo/Qodo-Embed-1-1.5B"]


class EmbeddingModelMeta(type):
    """Meta class for EmbeddingModel, ensure this is a Singleton"""

    _instances = {}

    def __call__(cls, *args, **kwargs) -> "EmbeddingModelMeta":
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class EmbeddingModel(metaclass=EmbeddingModelMeta):
    def __init__(self, denseModel=DENSE_MODELS[1]) -> None:
        self.denseModelName = denseModel
        # self.denseModel = HuggingFaceEmbeddings(model_name=self.denseModelName)
        print("Embedding modèle instancié correctement : " + denseModel)
        
    def getDenseModel(self) -> 'llm.models.EmbeddingModel':  # pragma: no cover
        #return self.denseModel
        return  llm.get_embedding_model("3-small")

    def embed_query(self, text) -> list[float]:
        return self.getDenseModel().embed(text)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self.embed_query(text) for text in texts]

    def cosine_distance(self, vector1:NDArray[Any], vector2:NDArray[Any])-> float: 
        return llm.cosine_similarity(vector1, vector2)
 
