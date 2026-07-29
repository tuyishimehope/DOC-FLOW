from openai import OpenAI

from app.core.config import settings

class OpenaiService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    async def generate_summary(self, content: str, instructions: str):
        response = self.client.responses.create(
            model="gpt-5.5",
            instructions=f"You are a senior writer at corporate company with 30 years of experience, summarize this text {instructions}",
            input=content
        )

        return response.output_text

    async def get_invoice_metadata(self, content: str, instructions: str):
        response = self.client.responses.create(
            model="gpt-5.5",
            instructions=f"{instructions}",
            input=content
        )

        return response.output_text

    async def get_contract_metadata(self, content: str, instructions: str):
        response = self.client.responses.create(
            model="gpt-5.5",
            instructions=f"{instructions}",
            input=content
        )

        return response.output_text
