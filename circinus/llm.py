import openai

from .settings import settings


class GPT:

    system_prompt = 'You are a helpful assistant.'

    def __init__(self, config=None):
        config = config or settings
        self.llm = openai.OpenAI(
            api_key=getattr(config, 'llm_api_key', 'ollama'),
            base_url=getattr(config, 'llm_base_url', 'http://localhost:11434/v1'),
            default_headers=self._default_headers(config),
        )
        self.model = getattr(config, 'llm_model', 'llama3.1')
        configured_fallbacks = getattr(config, 'llm_fallback_models', None)
        self.fallback_models = self._normalize_fallback_models(configured_fallbacks)
        self.max_tokens = getattr(config, 'max_tokens', 2048)
        self.temperature = 0

    @staticmethod
    def _default_headers(config) -> dict[str, str]:
        headers = {}
        site_url = getattr(config, 'llm_site_url', None)
        site_name = getattr(config, 'llm_site_name', None)
        if site_url:
            headers['HTTP-Referer'] = site_url
        if site_name:
            headers['X-Title'] = site_name
        return headers

    @staticmethod
    def _normalize_fallback_models(configured_fallbacks) -> list[str]:
        defaults = ['qwen3.5', 'llama3.1', 'mistral']
        if configured_fallbacks is None:
            return defaults
        if isinstance(configured_fallbacks, str):
            return [m.strip() for m in configured_fallbacks.split(',') if m.strip()]
        if isinstance(configured_fallbacks, (list, tuple)):
            return [str(m).strip() for m in configured_fallbacks if str(m).strip()]
        return defaults

    def _candidate_models(self) -> list[str]:
        models = [self.model]
        for model in self.fallback_models:
            if model not in models:
                models.append(model)
        return models

    def _system_msg(self, msg: str) -> dict[str, str]:
        return {'role': 'system', 'content': msg}

    def _user_msg(self, msg: str) -> dict[str, str]:
        return {'role': 'user', 'content': msg}

    def ask(self, msg: str) -> str:
        message = [self._system_msg(self.system_prompt), self._user_msg(msg)]
        models = self._candidate_models()
        for index, model in enumerate(models):
            try:
                rsp = self.llm.chat.completions.create(**self._cons_kwargs(message, model=model))
                return rsp.choices[0].message.content
            except openai.NotFoundError as exc:
                is_no_endpoint = 'No endpoints found' in str(exc)
                is_last_model = index == len(models) - 1
                if is_no_endpoint and not is_last_model:
                    continue
                raise

    def _cons_kwargs(self, messages: list[dict], model: str | None = None) -> dict:
        return {
            'messages': messages,
            'max_tokens': self.max_tokens,
            'n': 1,
            'stop': None,
            'temperature': self.temperature,
            'timeout': 3,
            'model': model or self.model
        }
