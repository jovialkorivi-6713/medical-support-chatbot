from fastapi.responses import StreamingResponse
from langchain_google_genai import ChatGoogleGenerativeAI
import asyncio

from app.core.config import settings
from app.llm.prompt_templates import get_chat_prompt_template
from app.models.chat import ChatSession

from app.llm.tools import get_medical_tools

class ChatEngine:
    def __init__(self):
        """
        Initialize Gemini LLM
        """

        base_llm = ChatGoogleGenerativeAI(
            model="gemini-flash-latest",
            temperature=0.7,
            google_api_key=settings.GEMINI_API_KEY,
            max_retries=0, # Fail immediately on quota errors instead of waiting
        )
        
        self.llm = base_llm.bind_tools(get_medical_tools)

        self.prompt = get_chat_prompt_template()

    def _build_memory_from_history(self, messages: list) -> list:
        """
        Convert MongoDB messages into LangChain Core Messages
        """
        from langchain_core.messages import HumanMessage, AIMessage
        
        chat_history = []

        for msg in messages:

            if msg.get("type") == "human":
                chat_history.append(
                    HumanMessage(content=msg.get("content", ""))
                )

            elif msg.get("type") == "ai":
                chat_history.append(
                    AIMessage(content=msg.get("content", ""))
                )

        return chat_history

    async def get_streaming_response(
        self,
        user_message: str,
        chat_session: ChatSession
    ):

        chat_history = self._build_memory_from_history(chat_session.messages)

        formatted_prompt = self.prompt.format_messages(
            chat_history=chat_history,
            input=user_message
        )

        async def generate():

            full_response = ""

            try:

                retries = 3

                for attempt in range(retries):

                    try:

                        async for chunk in self.llm.astream(formatted_prompt):

                            if chunk.content:
                                chunk_text = chunk.content
                                if isinstance(chunk_text, list):
                                    chunk_text = "".join([
                                        part.get("text", "") if isinstance(part, dict) else str(part)
                                        for part in chunk_text
                                    ])
                                elif not isinstance(chunk_text, str):
                                    chunk_text = str(chunk_text)
                                    
                                full_response += chunk_text
                                yield chunk_text

                        break

                    except Exception as e:
                        error_msg = str(e)
                        if "503" in error_msg or "429" in error_msg or "Quota" in error_msg:

                            if attempt < retries - 1:
                                await asyncio.sleep(5)
                                continue
                            else:
                                raise

                        else:
                            raise

                if not full_response.strip():

                    full_response = (
                        "I'm sorry, I couldn't generate a response."
                    )

                    yield full_response

            except Exception as e:

                error = str(e)

                if "429" in error:

                    full_response = (
                        "Rate limit exceeded.\n"
                        "Please wait a minute and try again."
                    )

                elif "503" in error:

                    full_response = (
                        "Gemini servers are currently busy.\n"
                        "Please try again after a few seconds."
                    )

                else:

                    full_response = (
                        f"Error generating response:\n{error}"
                    )

                yield full_response

            # Save User Message
            chat_session.messages.append(
                {
                    "type": "human",
                    "content": user_message
                }
            )

            # Save AI Response
            chat_session.messages.append(
                {
                    "type": "ai",
                    "content": full_response
                }
            )

            # Update chat title
            if len(chat_session.messages) == 2:

                if len(user_message) > 30:
                    chat_session.title = user_message[:30] + "..."
                else:
                    chat_session.title = user_message

            await chat_session.save()

        return StreamingResponse(
            generate(),
            media_type="text/event-stream"
        )


chat_engine = ChatEngine()