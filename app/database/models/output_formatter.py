from pydantic import BaseModel, Field

class IntentClassificationOutput(BaseModel):
    """
    Structured output model for the intent classification node.

    This model represents the classification result from the LLM when determining
    if a user's query is related to scheduling a meeting.

    Attributes:
        is_scheduling_intent (bool): Indicates whether the user's query has
        the intent to schedule a meeting.
    """
    is_scheduling_intent: bool = Field(
        description=(
            "True if the user's query is about scheduling a meeting, "
            "False if the query is unrelated to scheduling."
        )
    )