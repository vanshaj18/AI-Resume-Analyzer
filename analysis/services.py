# backend/services.py
from typing import Dict
import logging
import dotenv
from utils.logging_config import configure_logging
from .technical import technical_analysis
from .semantic import semantic_analysis
from .psychometric import psychometric_analysis
from .setup import get_llm_client, get_default_model
from .utils import parse_json_block
dotenv.load_dotenv()

configure_logging()
logger = logging.getLogger("backend.analysis")

DEFAULT_TEMPERATURE = 0.2

def run_full_analysis(
    text: str,
    model: str | None = None,
    temperature: float | None = None,
    threshold: int | None = None,
    criteria: dict | None = None,
    jd_prompt: str | None = None,
    task=None,
) -> Dict:
    client, provider = get_llm_client()
    default_model = get_default_model(provider)
    logger.debug(
        "run_full_analysis",
        extra={
            "provider": provider,
            "model": model or default_model,
            "temperature": temperature if temperature is not None else DEFAULT_TEMPERATURE,
            "text_length": len(text),
            "criteria": criteria,
            "jd_prompt": jd_prompt,
        },
    )
    
    model_config = {
        "client": client,
        "model": model or default_model,
        "temperature": DEFAULT_TEMPERATURE if temperature is None else temperature,
    }
    logger.debug("model_config", extra=model_config)

    try:
        technical = technical_analysis(
            {
                "text": text,
                "modelConfig": model_config,
                "threshold": threshold,
                "criteria": criteria,
                "jd_prompt": jd_prompt,
            },
            task=task,
        )
        semantic = semantic_analysis(
            {
                "text": text, 
                "modelConfig": model_config
            }, 
            task=task
        )
        psychometric = psychometric_analysis(
            {
                "text": text, 
                "modelConfig": model_config
            }, 
            task=task
        )
        
        res = _generate_full_summary(
            summary={
                "technical": technical,
                "semantic": semantic,
                "psychometric": psychometric
            }, 
            client=client, 
            model=model or "whisper-large-v3"
        )

        if res["status"] != 200:
            logger.debug("run_full_analysis", extra={"status": res["status"]})
            return {
                "summary": None,
                "score": 0,
                "status": 500
            }
        return {
            "summary": res["summary"],
            "score": res["score"],
        }
    except Exception as e:
        logger.exception("full_analysis_failed")
        return {
            "summary": None,
            "score": 0,
            "status": 500
        }


def _generate_full_summary(
    summary: dict,
    client,
    model: str,
) -> dict:
    logger.debug("generate_full_summary", extra={
        "semantic": summary["semantic"], 
        "techincal": summary["technical"], 
        "psychometric": summary["psychometric"]
    })
    try:
        completion = client.chat.completions.create(
            model=model,
            temperature=0.5,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert resume analyst. "
                        """ Return JSON object with keys:
                        - summary: 3-4 line combined summary with technical semantic psychometric
                        - score: (0-100)
                        """
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        "Generate a concise overall summary on the following.\n\n"
                        f"Semantic: {summary.get('semantic')}\n\n"
                        f"Technical: {summary.get('technical')}\n\n"
                        f"Psychometric: {summary.get('psychometric')}\n"
                    ),
                },
            ],
        )
        content = completion.choices[0].message.content or "{}"
        parsed = parse_json_block(content) or {}
        summary_text = parsed.get("summary")
        score = parsed.get("score")

        print(summary, score)
        if summary_text is None or score is None:
            raise ValueError("Invalid summary response from model.")

        return {
            "summary": summary_text,
            "score": int(score),
            "status": 200,
        }
    except Exception as exc:
        logger.exception("generate_full_summary_failed")
        return {
            "summary": None,
            "score": None,
            "status": 500,
            "error": str(exc),
        }
