#%%

import logging

from elevenlabs import generate
from langchain_openai import ChatOpenAI
from langchain.sql_database import SQLDatabase
from langchain.prompts import ChatPromptTemplate
from langchain_community.agent_toolkits import create_sql_agent

#%%

class AnswerWithVoice:

    def __init__(self, db_dilect_connection_uri:str, open_ai_api_key:str, eleven_api_key:str):
        self._chat_openai = ChatOpenAI(model="gpt-4-0125-preview", temperature=0, openai_api_key=open_ai_api_key)
        self._db = SQLDatabase.from_uri(db_dilect_connection_uri)
        self._eleven_api_key = eleven_api_key

    def _query_db(self, question:str) -> str:

        prefix = """Using the Postgres dialect, "performances", "films" and "upcoming_films" tables.
                    Join on "performances.film_id = films.film_id" to extract film titles.
                    Access performance dates and times via "performance_datetime" and "performance_date" in "performances".
                    Use "is_imax", "is_3d", and "is_ov" columns in "performances" to identify if a film is in IMAX, 3D, or English.
                    Movies in upcoming_films tables are not relesed yet. They are going to be released soon."""

        suffix = """Do not return sql statements. Return only the results.
                    Limit results to 10 rows."""

        agent_executor = create_sql_agent(self._chat_openai, db=self._db, agent_type="openai-tools", verbose=True, prefix=prefix, suffix=suffix)

        sql_output = agent_executor.invoke({"input": question})
        return sql_output.get("output")

    def _style_answer(self, sql_answer:str, user_name:str) -> str:

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

    def _generate_voice(self, answer:str) -> str:
        return generate(text=answer, voice="Callum", model="eleven_multilingual_v1", output_format = "mp3_44100_128", api_key=self._eleven_api_key)


    def answer(self, bot, message) -> str:
        # sourcery skip: extract-method

        user_name = message.from_user.first_name
        question = message.text

        sql_answer = self._query_db(question)
        logging.info(f"SQL Answer: {sql_answer}")

        styled_answer = self._style_answer(sql_answer, user_name)
        logging.info(f"Styled Answer: {styled_answer}")

        logging.info("Generating voice message ...")
        generate_voice = self._generate_voice(styled_answer)
        logging.info("Generated voice message!")

        logging.info(f"Sending the voice message to {message.chat.id}!")
        bot.send_voice(message.chat.id, generate_voice)
        logging.info(f"Voice message sent to {message.chat.id}!")

        del generate_voice
