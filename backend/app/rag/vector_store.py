import chromadb
from chromadb.config import Settings


class VectorStore:

    def __init__(self):

        self.client = chromadb.PersistentClient(
            path="chroma_db"
        )

        self.collection = self.client.get_or_create_collection(
            name="pdf_chat"
        )
    
    def add_chunks(self, chunks):

        # for chunk in chunks:
        #     print(chunk["embedding"][:10])  # Print the first 10 elements of the embedding for debugging

        self.collection.add(

            ids=[ str(chunk["chunk_id"])
                for chunk in chunks
            ],

            documents=[
                chunk["text"]
                for chunk in chunks
            ],

            embeddings=[
                chunk["embedding"]
                for chunk in chunks
            ],

            metadatas=[

                {
                    "page": chunk["page"],
                    "chunk_id": chunk["chunk_id"]
                }

                for chunk in chunks
            ]

        )

    
    def reset_collection(self):
        try:
            self.client.delete_collection("pdf_chat")
        except Exception:
            pass

        self.collection = self.client.create_collection("pdf_chat")
        
    ## raw Chroma response


    # def search(self, query_embedding,top_k=3):

    #     results = self.collection.query(
    #         query_embeddings=[query_embedding],
    #         n_results=top_k
    #     )

    #     return results
    

    ## Cleaner Chroma response

    
    def search(self, query_embedding,top_k=3):

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

        formatted_results = []

        for doc, metadata, distance in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            formatted_results.append({
                "text": doc,
                "page": metadata["page"],
                "distance": distance,
            })

        return formatted_results