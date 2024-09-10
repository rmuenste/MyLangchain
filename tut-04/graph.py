import os
from typing import TypedDict, Annotated, Sequence
import operator
from langchain_core.messages import BaseMessage
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import pyowm
from langchain_community.utilities import OpenWeatherMapAPIWrapper
from langgraph.graph import Graph
# Now you can access your environment variables using os.environ

load_dotenv(dotenv_path="../.env")

weather = OpenWeatherMapAPIWrapper()

# Set the model as ChatOpenAI
model = ChatOpenAI(temperature=0.5) 


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]

def function_1(state):
    messages = state['messages']
    user_input = messages[-1]
    complete_query = "Your task is to provide only the city name based on the user query. \
        Nothing more, just the city name mentioned. Following is the user query: " + user_input
    response = model.invoke(complete_query)
    state['messages'].append(response.content)
    print("Node1",state)
    return state

def function_2(state):
    messages = state['messages']
    agent_response = messages[-1]
    weather_data = weather.run(agent_response)
    state['messages'].append(weather_data)
    return state

def function_3(state):
    messages = state['messages']
    user_input = messages[0]
    available_info = messages[-1]
    complete_query = f"Your task is to provide info concisely based on the user query. \
                     Following is the user query: {user_input} and the available info: {available_info}."
    response = model.invoke(complete_query)
    state['messages'].append(response.content)
    print("Node3",state)
    return response.content

workflow = Graph()

#calling node 1 as agent
workflow.add_node("agent", function_1)
workflow.add_node("tool", function_2)
workflow.add_node("responder", function_3)


workflow.add_edge('agent', 'tool')
workflow.add_edge('tool', 'responder')

workflow.set_entry_point("agent")
workflow.set_finish_point("responder")

app = workflow.compile()

inputs = {"messages": ["What's the temperature in Las Vegas"]}
# Invoking it all at once
#resp = app.invoke("What's the temperature in Las Vegas")
#resp = app.invoke(inputs)
#print("Final reply:",resp)

#input = "What's the temperature in Las Vegas"
for output in app.stream(inputs):
    # stream() yields dictionaries with output keyed by node name
    for key, value in output.items():
        print(f"Output from node '{key}':")
        print("---")
        print(value)
    print("\n---\n")
