class RAGError(Exception):
    """Base exception for expected application failures."""
class DataValidationError(RAGError):
    """Input data did not match expected constraints."""
class RetrievalError(RAGError):
    """Retrieval failed or could not produce usable evidence."""
class ModelProviderError(RAGError):
    """An optional model provider could not return a valid response."""
