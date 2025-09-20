import os
from dotenv import load_dotenv
from agents import Agent, AgentBase, Runner,ModelSettings,RunContextWrapper, RunConfig, function_tool, OpenAIChatCompletionsModel, set_tracing_disabled
from openai import AsyncOpenAI
from pydantic import BaseModel
import asyncio
from dataclasses import dataclass
from agents.exceptions import MaxTurnsExceeded


# Load environment variables
load_dotenv()
GEMINI_MODEL = os.getenv("GEMINI_MODEL")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
BASE_URL = os.getenv("BASE_URL")

# Disable tracing for cleaner output
set_tracing_disabled(True)

client: AsyncOpenAI = AsyncOpenAI(api_key=GEMINI_API_KEY, base_url=BASE_URL)
model: OpenAIChatCompletionsModel = OpenAIChatCompletionsModel(GEMINI_MODEL, client)

# ----------------------------

@dataclass
class UserInfo:
    name: str
    gender: str
    

def custom_error(
    error: Exception,
    args: dict,
    context: RunContextWrapper | None,
    agent: AgentBase | None
) -> str:
    return f"tool failed due to: {str(error)}"

def fetch_weather(location: str):
    if location == "lofdsaljkfsd":  # simulate failure
        raise ValueError("Invalid location")
    return f"the weather of {location} is sunny"

@function_tool(strict_mode=True)
def say_hello(name: str = "Guest") -> str:
    """Greets a person by name."""
    return f"Hello {name}!"



def dynamic_instructions(wrapper: RunContextWrapper[UserInfo], agent: Agent[UserInfo]):
    boys_names = ["ali", "usman", "haider", "marjan", "sufyan", "ahmed"]
    
    for boy_name in boys_names:
        if wrapper.context.name == boy_name:
            return f"the user is {wrapper.context.gender} and his name is {wrapper.context.name}. display their UserInfo data."
    else:
        return f"the user is {wrapper.context.gender} and her name is {wrapper.context.name}. display their UserInfo data."


agent = Agent[UserInfo](
    name = "Helpful Agent",
    instructions="if the location is valid use 'fetch_weahter' tool for weather, invoke its custom error if locaiton is invalid",
    model=model,
    tools=[fetch_weather, say_hello],
)

def start():
    user_info = UserInfo(name="marjan", gender="male")
    result = Runner.run_sync(max_turns=1, starting_agent=agent, input="what is the weather of lofdsaljkfsd", context=user_info, run_config=RunConfig(model))
    print(result.final_output)