import os
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

def function_1(input_1):
    complete_query = "Your task is to provide only the city name based on the user query. \
        Nothing more, just the city name mentioned. Following is the user query: " + input_1
    response = model.invoke(complete_query)
    return response.content

def function_2(input_2):
    weather_data = weather.run(input_2)
    return weather_data


workflow = Graph()

#calling node 1 as agent
workflow.add_node("agent", function_1)
workflow.add_node("tool", function_2)

workflow.add_edge('agent', 'tool')

workflow.set_entry_point("agent")
workflow.set_finish_point("tool")

app = workflow.compile()
resp = app.invoke("What's the temperature in Las Vegas")
print(resp)