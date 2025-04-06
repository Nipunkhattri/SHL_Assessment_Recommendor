import json
from llama_index.core.schema import TextNode
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import VectorStoreIndex, StorageContext
from pinecone import Pinecone, ServerlessSpec
import os

class AssessmentIndexer:
    def __init__(self):
        self.api_key = os.getenv("PINECONE_API_KEY")
        self.environment = os.getenv("PINECONE_ENVIORNMENT_KEY")
        self.open_api_key = os.getenv("OPENAI_API_KEY")
        self.pc = Pinecone(api_key=self.api_key)

    def load_data(self, json_file_path):
        with open(json_file_path, encoding='utf-8') as f:
            data = json.load(f)
        
        nodes = []
        for item in data:
            text = item.get("description", "")
            metadata = {k: v for k, v in item.items() if k != "description"}
            node = TextNode(text=text, metadata=metadata)
            nodes.append(node)
        return nodes

    def initialize_pinecone(self):
        if 'shl-recommendor' not in self.pc.list_indexes().names():
            self.pc.create_index(
                name='shl-recommendor',
                dimension=1536,
                metric='cosine',
                spec=ServerlessSpec(
                    cloud='aws',
                    region=self.environment
                )
            )
        return PineconeVectorStore(index_name="shl-recommendor")

    def create_index(self, json_file_path):
        if 'shl-recommendor' not in self.pc.list_indexes().names():
            nodes = self.load_data(json_file_path)
            vector_store = self.initialize_pinecone()
            embed_model = OpenAIEmbedding(api_key=self.open_api_key, model="text-embedding-ada-002")
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
            index = VectorStoreIndex(nodes, storage_context=storage_context, embed_model=embed_model)
            
    def query(self, query_text):
        print("Querying for:", query_text)
        vector_store = self.initialize_pinecone()
        embed_model = OpenAIEmbedding(api_key=self.open_api_key, model="text-embedding-ada-002")
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        index = VectorStoreIndex.from_vector_store(vector_store=vector_store, storage_context=storage_context, embed_model=embed_model)
        retriever = index.as_retriever(
            similarity_top_k=10,
            score_threshold=0.0 
        )
        return retriever.retrieve(query_text)