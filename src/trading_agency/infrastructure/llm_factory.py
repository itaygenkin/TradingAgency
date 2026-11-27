import logging
import os
from typing import Optional

from langchain_core.runnables import Runnable
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel

from src.trading_agency.config import TEMPERATURE, MODELS

logger = logging.getLogger(__name__)

def get_analysis_model(structured_output_schema: Optional[type[BaseModel]] = None) -> Runnable:
    """
    Creates an LLM pipeline with sequential model fallbacks. When a schema is provided,
    every model in the fallback chain uses the same structured output schema.
    """
    models = MODELS

    def create_model(model_name: str) -> Runnable:
        chat_model = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=TEMPERATURE,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        if structured_output_schema is not None:
            return chat_model.with_structured_output(structured_output_schema, include_raw=True)
        return chat_model

    primary_model = create_model(models[0])

    # Every model after the first is tried in order if the preceding model fails.
    fallbacks: list[Runnable] = [create_model(model) for model in models[1:]]

    llm_with_fallback = primary_model.with_fallbacks(fallbacks=fallbacks)

    logger.info("LLM client initialized with primary model: {} and fallbacks: {}".format(primary_model, llm_with_fallback))
    return llm_with_fallback
