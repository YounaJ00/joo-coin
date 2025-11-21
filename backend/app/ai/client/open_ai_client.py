import json

from openai import OpenAI
from pandas import DataFrame

from app.ai.const.constans import BITCOIN_ANALYST_PROMPT, OPEN_AI_MODEL
from app.ai.dto.ai_analysis_response import AiAnalysisResponse


class OpenAIClient:
    def __init__(self) -> None:
        self.client = OpenAI()

    def get_bitcoin_trading_decision(self, df: DataFrame) -> AiAnalysisResponse:
        response = self.client.chat.completions.create(
            model=OPEN_AI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": [{"type": "text", "text": BITCOIN_ANALYST_PROMPT}],
                },
                {"role": "user", "content": [{"type": "text", "text": df.to_json()}]},
            ],
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content or "{}"
        result = AiAnalysisResponse.model_validate(json.loads(content))
        return result
