import os
from openai import AsyncOpenAI

class OpenAIAIRater:
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)

    async def rate_answer(self, question: str, golden_answer: str, predicted_answer: str) -> bool:
        LLM_PROMPT = """
        You are an AI assistant designed to evaluate the correctness of a predicted answer compared to a golden answer for a given question.
        Your task is to determine if the predicted answer is semantically equivalent or sufficiently similar to the golden answer to be considered correct.
        Respond with a JSON object containing a single key 'score' with a boolean value: true if the predicted answer is correct (semantically equivalent or very close to the golden answer), and false if it is incorrect.
        Do not provide any other text or explanation.

        Question: {question}
        Golden Answer: {golden_answer}
        Predicted Answer: {predicted_answer}
        """

        formatted_prompt = LLM_PROMPT.format(
            question=question,
            golden_answer=golden_answer,
            predicted_answer=predicted_answer
        )

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o", # Using a powerful model for good reasoning
                messages=[
                    {"role": "user", "content": formatted_prompt}
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "score_response",
                        "strict": True,
                        "schema": {
                            "type": "object",
                            "properties": {
                                "score": {
                                    "type": "boolean"
                                }
                            },
                            "required": ["score"],
                            "additionalProperties": False
                        }
                    }
                },
                verbosity="medium", # Added for better debugging if needed
            )
            import json
            response_content = json.loads(response.choices[0].message.content)
            return response_content.get("score", False)
        except Exception as e:
            print(f"An error occurred during AI rating: {e}")
            return False # Indicate an error with False
