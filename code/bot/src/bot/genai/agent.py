from __future__ import annotations

from typing import TYPE_CHECKING

from elevenlabs.client import ElevenLabs
from langchain.agents import create_agent
from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from loguru import logger

from bot.genai.db_tools import build_db_tools

if TYPE_CHECKING:
    import telebot
    from telebot import types


def _last_ai_content(messages: list) -> str:
    """Extract the final assistant answer from agent result messages."""
    for m in reversed(messages):
        if isinstance(m, AIMessage) and m.content:
            return m.content
    return "I couldn't find an answer."


# Default ElevenLabs voice ID (Rachel) when ELEVEN_VOICE_ID is not set. API requires UUID, not name.
_DEFAULT_ELEVEN_VOICE_ID = "ruirxsoakN0GWmGNIo04"


class AnswerWithVoice:
    def __init__(
        self,
        db_dialect_connection_uri: str,
        open_ai_api_key: str,
        eleven_api_key: str,
        eleven_voice_id: str | None = None,
    ) -> None:
        self._voice_id = eleven_voice_id or _DEFAULT_ELEVEN_VOICE_ID
        self._chat_openai = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            openai_api_key=open_ai_api_key,
        )
        self._eleven_api_key = eleven_api_key
        tools = build_db_tools(db_dialect_connection_uri)
        self._agent = create_agent(
            self._chat_openai,
            tools=tools,
            system_prompt=(
                "You are a cinema assistant. Use the tools to answer about films, showtimes, IMAX, 3D, OV (English), "
                "and dates. Be concise. Do not invent data; only report what the tools return."
            ),
        )

    def _query_db(self, question: str) -> str:
        result = self._agent.invoke({"messages": [{"role": "user", "content": question}]})
        return _last_ai_content(result["messages"])

    def _style_answer(self, sql_answer: str, user_name: str) -> str:
        template_string = """Style the following text to a very short and witty `voice message` from a friendly and funny and Shady Back Alley Ticket Scalper named `Mathias the ZKM guy`.
                            At the end, say something like `hit me up` if you want a ticket or I'll call me or similar to it in a cool way.
                            No more than 40 words.
                            If the movie is playing in imax or 3d, english, oversell it.
                            Do not use emojis.
                            Remove the bold and italic from the text too.
                            user name: ```{user_name}```
                            text: ```{sql_answer}```"""
        prompt_template = ChatPromptTemplate.from_template(template_string)
        styled_messages = prompt_template.format_messages(sql_answer=sql_answer, user_name=user_name)
        response = self._chat_openai.invoke(styled_messages)
        return response.content

    def _generate_voice(self, answer: str) -> bytes:
        client = ElevenLabs(api_key=self._eleven_api_key)
        chunks = client.text_to_speech.convert(
            voice_id=self._voice_id,
            text=answer,
            model_id="eleven_multilingual_v1",
            output_format="mp3_44100_128",
        )
        return b"".join(chunks)

    def answer(self, bot: telebot.TeleBot, message: types.Message) -> None:
        user_name = message.from_user.first_name
        question = message.text

        sql_answer = self._query_db(question)
        logger.info(f"SQL Answer: {sql_answer}")

        styled_answer = self._style_answer(sql_answer, user_name)
        logger.info(f"Styled Answer: {styled_answer}")

        logger.info("Generating voice message ...")
        generate_voice = self._generate_voice(styled_answer)
        logger.info("Generated voice message!")

        logger.info(f"Sending the voice message to {message.chat.id}!")
        bot.send_voice(message.chat.id, generate_voice)
        logger.info(f"Voice message sent to {message.chat.id}!")

        del generate_voice
