from pathlib import Path

from llama_index import OpenAIEmbedding
from llama_index.embeddings.base import BaseEmbedding
from llama_index.llms import OpenAI
from llama_index.llms.llm import LLM
from llama_index.storage.docstore import BaseDocumentStore, SimpleDocumentStore
from llama_index.storage.index_store import SimpleIndexStore
from llama_index.storage.index_store.types import BaseIndexStore

from circinus.logger import logger


Base = (Path(__file__).parent.parent / 'data').resolve(strict=True)


def _compatible_llm(config) -> LLM:
    return OpenAI(
        api_key=getattr(config, 'llm_api_key', 'ollama'),
        api_base=getattr(config, 'llm_base_url', 'http://localhost:11434/v1'),
        model=getattr(config, 'llm_model', 'llama3.1'),
        default_headers=_compatible_headers(config),
    )


def _compatible_headers(config) -> dict[str, str]:
    headers = {}
    site_url = getattr(config, 'llm_site_url', None)
    site_name = getattr(config, 'llm_site_name', None)
    if site_url:
        headers['HTTP-Referer'] = site_url
    if site_name:
        headers['X-Title'] = site_name
    return headers


def _compatible_embedding(config) -> BaseEmbedding:
    return OpenAIEmbedding(
        api_key=getattr(config, 'llm_api_key', 'ollama'),
        api_base=getattr(config, 'llm_base_url', 'http://localhost:11434/v1'),
        model=getattr(config, 'llm_embedding_model', 'nomic-ai/nomic-embed-text-v1.5'),
        default_headers=_compatible_headers(config),
    )


def llm_component(config) -> LLM:
    return _compatible_llm(config)


def embedding_component(config) -> BaseEmbedding:
    return _compatible_embedding(config)


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
