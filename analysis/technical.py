
from typing import Optional
from analysis.types import TechnicalAnalysisInput, TechnicalAnalysisOutput
import logging
from analysis.utils import _coerce_to_str, parse_json_block, retry_policy
from groq import RateLimitError
logger = logging.getLogger("backend.analysis.technical")

def technical_analysis(
    input: TechnicalAnalysisInput,
    task=None,
) -> TechnicalAnalysisOutput:
    logger.debug("semantic_analysis_request", extra={"input": input})

    model_config = input.get("modelConfig", {})
    client = model_config["client"]
    model = model_config.get("model", "llama-3.1-8b-instant")
    temperature = model_config.get("temperature", 0.2)
    threshold = input.get("threshold", 70)
    # criteria = input.get("criteria") or {}
    jd_prompt = input.get("jd_prompt")
    text = input.get("text", "")

    # log the model configuration being used
    logger.debug("technical_analysis_model_config", extra={"model": model, "temperature": temperature, "threshold": threshold})

    try:
        completion = client.chat.completions.create(
            model=model,
            temperature=temperature,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an EXPERT in analysing technical details from text."

                        """RETURN FORMAT: JSON
                        - technicalSummary: A 2 line summary technical details.
                        - skillMatch: MAX 3 of the skills mentioned in the document with .
                        - experienceLevel: An overall true experience level classification (Junior, Mid, Senior, Manager, CTO, COO).
                        - overallScore: A score representing the overall technical fit. (0-100)"""
                        "Evaluation Criteria (optional):\n"
                        f"- Job Description: {jd_prompt}\n\n"
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        "Analyze the following text to understand its "
                        "technical details, identify mentioned skills, determine overall experience level"
                        "and calculate the overall technical score.\n\n"
                        f"Document Text:\n{text}\n\n"
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
        logger.debug("technical_analysis_response", extra={"response": completion.choices[0].message.content})
        content = completion.choices[0].message.content or "{}"
        parsed = parse_json_block(content)
        validated = as_technical_analysis_response(parsed)
        return {
            "technicalSummary": validated["technicalSummary"],
            "skillMatch": validated["skillMatch"],
            "experienceLevel": validated["experienceLevel"],
            "overallScore": validated["overallScore"],
            "error": None,
            "code": 200
        }
    
    except Exception as e:
        logger.exception("semantic_analysis_parsing_failed")
        return {
            "technicalSummary": None,
            "skillMatch": None,
            "experienceLevel": None,
            "overallScore": None,
            "error": str(e),
            "code": 500
        }


def as_technical_analysis_response(
    value,
) -> Optional[TechnicalAnalysisOutput]:
    logger.debug("validating_technical_analysis_response", extra={"value": value})
    value = _coerce_to_str(value)
    if not value:
        return None
    return {
        "technicalSummary": value["technicalSummary"],
        "skillMatch": value["skillMatch"],
        "experienceLevel": value["experienceLevel"],
        "overallScore": value["overallScore"],
    }
