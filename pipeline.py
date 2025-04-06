import json
from llama_index.core.schema import TextNode
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import VectorStoreIndex, StorageContext
from pinecone import Pinecone, ServerlessSpec
import os
import re
from llama_index.llms.openai import OpenAI

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
            text_parts = [
                f"Assessment Name: {item.get('name', '')}",
                f"Description: {item.get('description', '')}",
                f"Duration: {item.get('duration', '')}",
                f"Test Types: {', '.join(item.get('TestTypes', []))}",
                f"Remote Testing: {item.get('RemoteTesting', '')}",
                f"Adaptive Support: {item.get('Adaptive/IRT Support', '')}"
            ]
            text = " | ".join(text_parts)
            metadata = {k: v for k, v in item.items()}
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

    def extract_duration_from_query(self, query: str) -> int:
        """
        Extracts the duration in minutes from the user query.
        Returns -1 if not found.
        """
        match = re.search(r"(\d+)\s*(minutes|min|minute|hours|hour)", query.lower())
        if match:
            value = int(match.group(1))
            unit = match.group(2)
            if "hour" in unit:
                return value * 60
            return value
        return -1

    def rerank_with_gpt(self, query: str, results):
        """
        Rerank the results using GPT based on relevance to the query.
        """
        descriptions = [f"{i+1}. {res.node.text}" for i, res in enumerate(results)]

        llm = OpenAI(api_key=self.open_api_key, model="gpt-4o")

        prompt = f"""
        You are an assistant helping a recruiter choose the best assessments for their hiring needs.

        Query: "{query}"

        Here are the assessments:
        {chr(10).join(descriptions)}

        Rank the top 10 most relevant assessments based on the query.
        Return only the rank numbers (1 to N) in sorted order, separated by commas.
        """

        gpt_response = llm.complete(prompt)

        print("GPT Response:", gpt_response)
        content = gpt_response.text.strip()
        print("GPT Ranking Response:", content)

        try:
            indices = [int(x.strip()) - 1 for x in content.split(',') if x.strip().isdigit()]
            return [results[i] for i in indices if 0 <= i < len(results)]
        except Exception as e:
            print("Error in reranking:", e)
            return results[:10]

    def query(self, query_text):
        """
        Process the query and return the top 10 most relevant assessments.
        """
        duration_limit = self.extract_duration_from_query(query_text)
        print("Duration Limit:", duration_limit)

        vector_store = self.initialize_pinecone()  
        embed_model = OpenAIEmbedding(api_key=self.open_api_key, model="text-embedding-ada-002")

        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        index = VectorStoreIndex.from_vector_store(vector_store=vector_store, storage_context=storage_context, embed_model=embed_model)

        retriever = index.as_retriever(similarity_top_k=30)
        results = retriever.retrieve(query_text)

        if duration_limit != -1:
            filtered = []
            for result in results:
                try:
                    dur = int(result.node.metadata.get("duration", "0").split()[0])
                    if dur <= duration_limit:
                        filtered.append(result)
                except Exception as e:
                    print(f"Skipping result due to duration parse error: {e}")
                    continue
        else:
            filtered = results

        print("Filtered Results:", filtered)

        top_10 = self.rerank_with_gpt(query_text, filtered)
        return top_10