from typing import Optional
from analysis.utils import _coerce_to_str, parse_json_block, retry_policy
from groq import RateLimitError
from .types import SemanticAnalysisInput, SemanticAnalysisOutput
import logging
logger = logging.getLogger("backend.analysis.semantic")


def semantic_analysis(
    input: SemanticAnalysisInput,
    task=None,
) -> SemanticAnalysisOutput:
    # Log the incoming request
    logger.debug("semantic_analysis_request", extra={"input": input})

    model_config = input.get("modelConfig", {})
    client = model_config["client"]
    model = model_config.get("model", "llama-3.1-8b-instant")
    temperature = model_config.get("temperature", 0.2)

    # log the model configuration being used
    logger.debug("semantic_analysis_model_config", extra={"model": model, "temperature": temperature})

    try:
        completion = client.chat.completions.create(
            model=model,
            temperature=temperature,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert in analysing semantic analysis."
                        """RETURN FORMAT: JSON Object with
                        - semanticSummary: A 2-3 line summary of the document's meaning and implications.
                        - keyThemes: A list of the main themes or topics present in the document. MAX 3
                        - overallSentiment: An overall sentiment classification (e.g., Positive, Negative, Neutral)
                        """
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        "Analyze the following document text to understand its "
                        "contextual meaning, identify key themes, and determine "
                        "the overall sentiment.\n\n"
                        f"Document Text:\n{input['text']}\n\n"
                        "Return JSON only."
                    ),
                },
            ],
        )
    except RateLimitError as exc:
        if task is not None:
            return retry_policy(task, exc, "rate_limit")
        raise
    # log response 
    try: 
        logger.debug("semantic_analysis_response", extra={"response": completion.choices[0].message.content})
        content = completion.choices[0].message.content or "{}"
        parsed = parse_json_block(content)
        validated = as_semantic_analysis_response(parsed)
        return {
            "semanticSummary": validated["semanticSummary"],
            "keyThemes": validated["keyThemes"],
            "overallSentiment": validated["overallSentiment"],
            "error": None,
            "code": 200
        }
    
    except Exception as e:
        logger.exception("semantic_analysis_parsing_failed")
        return {
            "semanticSummary": None,
            "keyThemes": None,
            "overallSentiment": None,
            "error": str(e),
            "code": 500
        }


def as_semantic_analysis_response(
    value,
) -> Optional[SemanticAnalysisOutput]:
    logger.debug("validating_semantic_analysis_response", extra={"value": value})
    value = _coerce_to_str(value)
    if not value:
        return None
    return {
        "semanticSummary": value["semanticSummary"],
        "keyThemes": value["keyThemes"],
        "overallSentiment": value["overallSentiment"],
    }
