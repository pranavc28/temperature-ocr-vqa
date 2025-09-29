import os
from openai import AsyncOpenAI
import base64
import io
from PIL import Image
from typing import Union, List

class OpenAIVQAModel:
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)

    def _encode_image_to_base64(self, image_bytes: bytes) -> str:
        """Encodes image bytes to a base64 string."""
        return base64.b64encode(image_bytes).decode("utf-8")

    async def query_image(self, image: Union[bytes, Image.Image], questions: List[str], temperature: float | None = 0.0) -> List[str]:
        """
        Queries the OpenAI Vision model with an image and a list of questions.

        Args:
            image (Union[bytes, Image.Image]): The image to query, either as bytes or a PIL Image object.
            questions (List[str]): A list of questions to ask about the image.

        Returns:
            List[str]: A list of the model's answers to the questions.
        """
        try:
            if isinstance(image, Image.Image):
                byte_stream = io.BytesIO()
                # Assuming JPEG, adjust format if needed (e.g., "PNG")
                image.save(byte_stream, format="JPEG")
                image_bytes = byte_stream.getvalue()
            else:
                image_bytes = image

            base64_image = self._encode_image_to_base64(image_bytes)

            # Construct the content for the API call
            content_blocks = [
                {"type": "text", "text": "Please answer the following questions about the image in a numbered list format, one answer per question."},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}",
                    },
                },
            ]
            for i, question in enumerate(questions):
                content_blocks.append({"type": "text", "text": f"{i+1}. {question}"})

            response = await self.client.chat.completions.create(
                model="gpt-4o",  # Or another vision-capable model
                messages=[
                    {
                        "role": "user",
                        "content": content_blocks,
                    }
                ],
                temperature=temperature,
                max_tokens=500, # Increased max_tokens to accommodate multiple answers
            )

            # Process the model's response
            full_response_content = response.choices[0].message.content
            # Assuming the model returns a numbered list, parse it into a list of strings
            answers = [line.strip() for line in full_response_content.split('\n') if line.strip().startswith(tuple(str(i) + '.' for i in range(1, len(questions) + 1)))]
            # Further refinement may be needed based on actual model output format
            return answers
        except Exception as e:
            return [f"An error occurred: {e}"]

    async def cluster_questions_by_creativity(self, questions_data: dict) -> dict:
        """
        Clusters questions based on their creativity level using an LLM.

        Args:
            questions_data (dict): A dictionary where keys are temperature values and values are dictionaries of questions with their accuracy data.

        Returns:
            dict: A dictionary with cluster names as keys and lists of questions as values.
        """
        try:
            # Flatten the questions from all temperature data
            all_questions = set()
            for temp, questions in questions_data.items():
                all_questions.update(questions.keys())
            
            all_questions = list(all_questions)

            # Prepare the prompt for the LLM
            prompt = """
            You are an AI assistant tasked with clustering questions based on their creativity and complexity level. 
            Create exactly 5 clusters that represent different levels of creativity and complexity:
            
            1. Binary_Factual_Questions: Simple yes/no questions about specific categories or facts
            2. Identification_Questions: Questions asking to identify specific information (author, title, etc.)
            3. Classification_Questions: Questions asking about type or genre with some interpretation needed
            4. Analytical_Questions: Questions requiring more nuanced understanding and analysis
            5. Creative_Subjective_Questions: Open-ended questions requiring creative thinking or subjective judgment
            
            Analyze each question and assign it to the most appropriate cluster based on:
            - How much creativity is required to answer
            - Whether it's binary (yes/no) vs open-ended
            - Level of interpretation and analysis needed
            - Factual vs subjective nature
            
            Return a JSON object with exactly these 5 cluster names as keys: "Binary_Factual_Questions", "Identification_Questions", "Classification_Questions", "Analytical_Questions", "Creative_Subjective_Questions".
            Each key should have an array of questions as its value.
            Make sure each question appears in exactly one cluster.
            
            Questions to cluster:
            """

            # Add questions to the prompt
            for i, question in enumerate(all_questions, 1):
                prompt += f"{i}. {question}\n"

            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "question_clusters",
                        "strict": True,
                        "schema": {
                            "type": "object",
                            "properties": {
                                "Binary_Factual_Questions": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                },
                                "Identification_Questions": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                },
                                "Classification_Questions": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                },
                                "Analytical_Questions": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                },
                                "Creative_Subjective_Questions": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                }
                            },
                            "required": ["Binary_Factual_Questions", "Identification_Questions", "Classification_Questions", "Analytical_Questions", "Creative_Subjective_Questions"],
                            "additionalProperties": False
                        }
                    }
                },
                temperature=0.3,
                max_tokens=2000
            )

            # Parse the response
            import json
            clusters = json.loads(response.choices[0].message.content)
            return clusters
        except Exception as e:
            print(f"An error occurred during clustering: {e}")
            return {}
