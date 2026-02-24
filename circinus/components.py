from functools import partial
from pathlib import Path

from llama_index import MockEmbedding, OpenAIEmbedding
from llama_index.embeddings.base import BaseEmbedding
from llama_index.llms import MockLLM, OpenAI
from llama_index.llms.llm import LLM
from llama_index.storage.docstore import BaseDocumentStore, SimpleDocumentStore
from llama_index.storage.index_store import SimpleIndexStore
from llama_index.storage.index_store.types import BaseIndexStore

from circinus.logger import logger


Base = (Path(__file__).parent.parent / 'data').resolve(strict=True)


class MockLLMAdapter:
    """Adapter to make MockLLM compatible with GPT interface"""
    def __init__(self, mock_llm):
        self._llm = mock_llm
        self.temperature = 0
        self.system_prompt = 'You are a helpful assistant.'
        self.query_wrapper_prompt = 'Query: {query}'
        self.pydantic_program_mode = 'default'
        self.model_name = 'mock'
        self.context_window = 4096
        self.metadata = type('obj', (object,), {
            'context_window': 4096,
            'num_output': 256,
            'is_chat_model': False,
            'is_function_calling_model': False,
        })()
    
    def ask(self, message: str) -> str:
        """Mimics GPT.ask() interface"""
        return (
            "Here is a mock snippet:\n"
            "```python\n"
            "def mock_function(x, y):\n"
            "    return x + y\n"
            "```"
        )


def _openai_llm(config):
    return OpenAI(api_key=config.openai_api_key)


def _mock_llm() -> LLM:
    return MockLLMAdapter(MockLLM())


def _openai_embedding(config):
    return OpenAIEmbedding(api_key=config.openai_api_key)


def _mock_embedding():
    return MockEmbedding(384)


def llm_component(config) -> LLM:
    return {
        'openai': partial(_openai_llm, config),
        'mock': _mock_llm,
    }[config.mode]()


def embedding_component(config) -> BaseEmbedding:
    return {
        'openai': partial(_openai_embedding, config),
        'mock': _mock_embedding,
    }[config.mode]()


def index_store_component() -> BaseIndexStore:
    try:
        return SimpleIndexStore.from_persist_dir(persist_dir=str(Base))
    except FileNotFoundError:
        logger.debug('Local index store not found, creating a new one')
        return SimpleIndexStore()


def doc_store_component() -> BaseDocumentStore:
    try:
        return SimpleDocumentStore.from_persist_dir(persist_dir=str(Base))
    except FileNotFoundError:
        logger.debug('Local document store not found, creating a new one')
        return SimpleDocumentStore()
