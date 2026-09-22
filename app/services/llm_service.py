from langchain_ollama import ChatOllama


class LLMService:

    def __init__(self):
        self.llm = ChatOllama(
            model="llama3.2",
            temperature=0
        )

    async def generate_response(self, messages) -> str:

        response = await self.llm.ainvoke(messages)

        return response.content


llm_service = LLMService()

