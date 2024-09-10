import os
#https://github.com/langchain-ai/langgraph/blob/main/examples/rag/langgraph_agentic_rag.ipynb
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import pyowm
from langchain_community.utilities import OpenWeatherMapAPIWrapper
from langgraph.graph import Graph
from langgraph.graph.message import add_messages 
from langchain_core.messages import AIMessage, HumanMessage, BaseMessage
from typing import TypedDict, Annotated, Sequence
from langgraph.graph import StateGraph, END
from langchain_core.utils.function_calling import convert_to_openai_function
from langchain_community.tools.openweathermap import OpenWeatherMapQueryRun
from langchain_core.utils.function_calling import convert_to_openai_function
from langgraph.prebuilt import ToolInvocation
import json
from langchain_core.messages import FunctionMessage
from langgraph.prebuilt import ToolExecutor
# Now you can access your environment variables using os.environ

load_dotenv(dotenv_path="../.env")

# Set the model as ChatOpenAI
model = ChatOpenAI(temperature=0.5) 

weather = OpenWeatherMapAPIWrapper()

tools = [OpenWeatherMapQueryRun()]

functions = [convert_to_openai_function(function) for function in tools]

model = model.bind_functions(functions)



class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

tool_executor = ToolExecutor(tools)

def function_1(state):
    messages = state["messages"]
    user_input = messages[-1].content
    complete_query = "Your task is to provide only the city name based on the user query. \
        Nothing more, just the city name mentioned. Following is the user query: " + user_input
    response = model.invoke(complete_query)
    return {"messages": [AIMessage(content=response.content)]}

def function_2(state):
    messages = state["messages"]
    lastMessage = messages[-1]

    parsed_tool_input = json.loads(lastMessage.additional_kwargs["function_call"]["arguments"])



def function_3(state):
    messages = state["messages"]
    input_3 = messages[-1]
    print(f"This is input_3 = {input_3}")
    complete_query = f"In the input: {input_3} you are provided with weather data of a certain city. From this data formulate a reply that tells the user the temperate in that city."
    response = model.invoke(complete_query)
    return {"messages": [response.content]}



workflow = StateGraph(AgentState)

#calling node 1 as agent
workflow.add_node("agent", function_1)
workflow.add_node("tool", function_2)
workflow.add_node("filter", function_3)

workflow.add_edge('agent', 'tool')
workflow.add_edge('tool', 'filter')

workflow.set_entry_point("agent")
workflow.set_finish_point("filter")

app = workflow.compile()
#resp = app.invoke("What's the temperature in Las Vegas")
#print(resp)
#
input: AgentState = {
    "messages":[HumanMessage(content="What's the temperature in Las Vegas")]
}
for output in app.stream(input):
    # stream() yields dictionaries with output keyed by node name
    for key, value in output.items():
        print(f"Output from node '{key}':")
        print("---")
        print(value)
    print("\n---\n")