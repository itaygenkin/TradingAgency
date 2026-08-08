import logging
import os

from langchain_core.language_models import BaseLanguageModel, BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI

from src.config import TEMPERATURE, MODELS

logger = logging.getLogger(__name__)

def get_analysis_model() -> BaseChatModel:
    """
    Creates a Runnable LLM pipeline with robust sequential fallbacks. If the primary model fails
    (Rate-Limit, Quota exhaustion, Server Error), LangChain will seamlessly retry with the backup models.
    """
    models = MODELS
    primary_model = ChatGoogleGenerativeAI(
        model=models[0],
        temperature=TEMPERATURE,
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )

    fallback_model = ChatGoogleGenerativeAI(
        model=models[1],
        temperature=TEMPERATURE,
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )

    # hierarchical fallback
    fallbacks: list[BaseLanguageModel] = [fallback_model]

    llm_with_fallback = primary_model.with_fallbacks(fallbacks=fallbacks)

    logger.info("LLM client initialized with primary model: {} and fallbacks: {}".format(primary_model, llm_with_fallback))
    return llm_with_fallback


