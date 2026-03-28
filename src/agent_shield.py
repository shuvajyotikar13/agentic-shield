import redis
import numpy as np
import time
from sentence_transformers import SentenceTransformer
from redis.commands.search.query import Query

class SemanticShield:
    def __init__(self):
        print("Loading Embedding Model (all-MiniLM-L6-v2)...")
        self.r = redis.Redis(host='localhost', port=6379, decode_responses=False)
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index_name = "idx:malicious_prompts"

    def check_threat(self, prompt: str):
        start_time = time.time()
        
        # Embed the incoming prompt
        embedding = self.model.encode(prompt).astype(np.float32).tobytes()
        
        # Search Redis for the closest semantic match
        query = (
            Query("*=>[KNN 1 @vector $vec AS score]")
            .sort_by("score")
            .return_fields("score", "pattern")
            .dialect(2)
        )
        
        results = self.r.ft(self.index_name).search(query, {"vec": embedding})
        latency = (time.time() - start_time) * 1000
        
        if results.docs:
            score = float(results.docs[0].score)

            # --- ADD THIS LINE FOR THE DEMO ---
            print(f"   -> [DEBUG] Semantic Distance Score: {score:.4f}")

            # Relaxed Threshold: 0.45 (Catches broader intent)
            if score < 0.75:
                return True, results.docs[0].pattern, latency

        return False, None, latency
