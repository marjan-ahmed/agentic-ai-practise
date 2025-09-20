import os
from dotenv import load_dotenv
from agents import Agent, Runner, enable_verbose_stdout_logging, RunConfig, HandoffInputData, function_tool, OpenAIChatCompletionsModel, set_tracing_disabled, handoff
from openai import AsyncOpenAI
from pydantic import BaseModel
from typing import List
import asyncio
from agents.extensions import handoff_filters
from agents import RunContextWrapper
import pprint

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

# class UserContext(BaseModel):
#     name: str
    
# def dynamic_instructions(
#     context: RunContextWrapper[UserContext], agent: Agent[UserContext]
# ) -> str:
#     return f"The user's name is {context.context.name}. Help them with their questions."



# class Answer(BaseModel):
#     word_count: int
#     answer: str

# @function_tool
# def movie_list(movies: str) -> List:
#     """Return a list of comma seperated movie"""
#     return movies

# def custom_error(tool_name: str, error: Exception) -> str:
#     return f"Oops! {tool_name} failed because {error}"

# @function_tool(
#     name_override="weather_finder",
#     description_override="Return the weather of a country only ",
#     docstring_style='google',
#     use_docstring_info=False,
#     failure_error_function=custom_error,
#     strict_mode=True
#     )
# def weather_forecast(city: str) -> str:
#     """Return the weather of a city"""
#     return f"{city} is sunny"

# waiter: Agent = Agent(
#     name="waiter agent", 
#     instructions=(
#        dynamic_instructions
#     ),
#     model=model,
# )


# agent: Agent = Agent[UserContext](
#     name="Helpful Assistant",
#     instructions=(
#         "You're a helpful assistant. first greet user with their name from context"
#         "When the user inputs movies with comma separated values, use `movie_list` tool. "
#         "When user wants to ask weather of a provided city, use `weather_forecast` tool. "
#         "For food questions, handoff to the waiter agent."
#     ),
#     model=model,
#     tools=[weather_forecast, movie_list],
#     handoffs=[
#         handoff(
#             agent=waiter,
#             tool_description_override="Send to waiter for food-related queries",
#             tool_name_override="food_handoff",
#             input_filter=handoff_filters.remove_all_tools
#         )
#         ],
# )


# async def main() -> None:
#     context = UserContext(name="Marjan")
#     prompt = "what is pasta?"
#     result = await Runner.run(agent, prompt, run_config=RunConfig(model), context=context)
#     print(result.final_output)



# def simple_filter(data: HandoffInputData) -> HandoffInputData:
#     print("\n\n[HANDOFF] Summarizing news transfer...\n\n")
#     summarized_conversation = "Get latest tech news."
    
#     print("\n\n[ITEM 1]", data.input_history)
#     print("\n\n[ITEM 2]", data.pre_handoff_items)
#     print("\n\n[ITEM 1]", data.new_items)
    
#     return HandoffInputData(
#         input_history=summarized_conversation,
#         pre_handoff_items=(),
#         new_items=(),
#     )
# @function_tool
# def get_weather(city: str) -> str:
#     """A simple function to get the weather for a user."""
#     return f"The weather for {city} is sunny."
# # Agent 1 (news agent)
# news_agent = Agent(
#     name="NewsAgent",
#     instructions="give the latest the news about user topic.",
#     handoff_description="this agents is use for giving the news ",
#     tools = [get_weather],
#     model=model,
# )

# # Agent 2 (main agent)
# main_agent = Agent(
#     name="MainAgent",
#     instructions="you are the main agent first generate answer then handoffs to newsagent.",
#     model=model,
#     tools = [get_weather],
#     handoffs=[
#         handoff(agent=news_agent, input_filter=simple_filter)],  # pyright: ignore[reportUndefinedVariable]
# )

# def main():
#     res = Runner.run_sync(main_agent, "what is the weather in karachi and also what is the news of today", run_config= RunConfig(model = model))
#     print("\n👉 Final Response:", res.final_output)
#     print("\n👉 Final agent:", res.last_agent.name)

# def start():
#     main()

enable_verbose_stdout_logging()

@function_tool(is_enabled=True)
def fetch_weather(location: str) -> str:
    """Provide Weather Information Based On Location."""
    print('tool called')
    print(f"DEBUG: fetch_weather tool called for location: {location}")
    return f"the weather of {location} is sunny"


agent :Agent = Agent(
    name = "Joke agent", 
    instructions = "You are a joking agent return joke and also check if user ask about weather then use weather tool",
    model= model,
    tools=[fetch_weather],
    # tool_use_behavior="stop_on_first_tool"
    )
async def main():
    
    result = await Runner.run(
    agent, 
    "hello tell me a short joke in roman urdu also tell me weather in karachi", 
    run_config= RunConfig(model=model), 
    max_turns= 3
    )
    
    pprint.pprint(result.final_output)
    print(type(result.final_output))
def start():
    asyncio.run(main())