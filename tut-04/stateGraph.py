
import os
from typing import TypedDict, Annotated, Sequence
import operator
from langchain_core.messages import BaseMessage
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import Graph, StateGraph 


load_dotenv(dotenv_path="../.env")

# Create the llm structure
model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.5)
#model = ChatOpenAI(model="gpt-4")

