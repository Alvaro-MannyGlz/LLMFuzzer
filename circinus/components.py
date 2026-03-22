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


def _openrouter_llm(config) -> LLM:
    return OpenAI(
        api_key=config.openrouter_api_key,
        api_base=config.openrouter_base_url,
        model=config.openrouter_api_model,
        default_headers={
            'HTTP-Referer': config.openrouter_site_url,
            'X-Title': config.openrouter_site_name,
        },
    )


def _openrouter_embedding(config) -> BaseEmbedding:
    return OpenAIEmbedding(
        api_key=config.openrouter_api_key,
        api_base=config.openrouter_base_url,
        model=config.openrouter_embedding_model,
        default_headers={
            'HTTP-Referer': config.openrouter_site_url,
            'X-Title': config.openrouter_site_name,
        },
    )


def llm_component(config) -> LLM:
    return _openrouter_llm(config)


def embedding_component(config) -> BaseEmbedding:
    return _openrouter_embedding(config)


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
