"""
Semantic search using embeddings (Bonus Feature)
"""
from typing import List, Dict, Tuple, Any
import logging
import numpy as np

logger = logging.getLogger(__name__)

try:
    from sentence_transformers import SentenceTransformer
    import faiss
    HAS_EMBEDDINGS = True
except ImportError:
    HAS_EMBEDDINGS = False
    logger.warning("sentence-transformers or faiss not installed.")


class SemanticSearchEngine:
    """Semantic search over extracted clauses"""
    
    def __init__(self, model_name: str = "sentence-transformers/all-mpnet-base-v2"):
        if not HAS_EMBEDDINGS:
            raise RuntimeError("Dependencies not installed. Install requirements to use semantic search.")
        
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.index: Any = None  # FAISS index type hint
        self.clauses: List[str] = []
        self.metadata: List[Dict[str, Any]] = []
    
    def build_index(self, results: List[Dict[str, Any]]) -> None:
        """Build FAISS index from extracted clauses"""
        for result in results:
            contract_id = result.get('contract_id', 'unknown')
            
            for clause_type in ['termination_clause', 'confidentiality_clause', 'liability_clause']:
                clause_text = result.get(clause_type, '')
                
                if clause_text and clause_text not in ['Not found', 'Error', None]:
                    self.clauses.append(clause_text)
                    self.metadata.append({
                        'contract_id': contract_id,
                        'clause_type': clause_type,
                        'text': clause_text
                    })
        
        if not self.clauses:
            logger.warning("No clauses to index")
            return
        
        logger.info(f"Encoding {len(self.clauses)} clauses...")
        
        embeddings = self.model.encode(
            self.clauses,
            show_progress_bar=True,
            convert_to_numpy=True
        )
        
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)
        faiss.normalize_L2(embeddings)
        self.index.add(embeddings.astype('float32'))
        
        logger.info(f"Index built with {self.index.ntotal} clauses")
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar clauses"""
        if self.index is None:
            raise ValueError("Index not built. Call build_index() first.")
        
        # Encode query
        query_embedding: np.ndarray = self.model.encode([query], convert_to_numpy=True)
        faiss.normalize_L2(query_embedding)
        
        # Search - type: ignore to suppress Pylance warning
        scores, indices = self.index.search(
            query_embedding.astype('float32'), top_k
        )  # type: ignore[call-arg]
        
        # Prepare results
        results: List[Dict[str, Any]] = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.metadata):
                result = self.metadata[idx].copy()
                result['score'] = float(score)
                results.append(result)
        
        return results
