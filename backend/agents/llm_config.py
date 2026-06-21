from langchain_google_genai import ChatGoogleGenerativeAI
import os
import time


def get_llm():
    api_key = os.getenv("GEMINI_API_KEY", "")
    model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    return ChatGoogleGenerativeAI(
        model=model,
        google_api_key=api_key,
        temperature=0.7,
    )


def invoke_with_retry(chain, inputs, retries=3, delay=2):
    """Retry LLM calls on transient API errors (503, rate limits)."""
    last_error = None
    for attempt in range(retries):
        try:
            return chain.invoke(inputs)
        except Exception as e:
            last_error = e
            err = str(e).lower()
            if attempt < retries - 1 and ("503" in err or "429" in err or "unavailable" in err):
                time.sleep(delay * (attempt + 1))
                continue
            raise
    raise last_error
