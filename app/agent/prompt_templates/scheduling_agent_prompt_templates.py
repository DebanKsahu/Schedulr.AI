from langchain.prompts import ChatPromptTemplate

from app.agent.prompts.scheduling_agent_prompts import (
    system_message_prompt_intent_validation,
    human_message_prompt_intent_validation,
    system_message_prompt_entity_extraction,
    human_message_prompt_entity_extraction,
    system_message_prompt_about_schedule_response,
    human_message_prompt_about_schedule_response
)

intent_validation_template = ChatPromptTemplate([
    ("system", system_message_prompt_intent_validation),
    ("human", human_message_prompt_intent_validation)
])

entity_extraction_template = ChatPromptTemplate([
    ("system", system_message_prompt_entity_extraction),
    ("human", human_message_prompt_entity_extraction)
])

schedule_response_template = ChatPromptTemplate([
    ("system", system_message_prompt_about_schedule_response),
    ("human", human_message_prompt_about_schedule_response)
])