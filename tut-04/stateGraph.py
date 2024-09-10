
import os
from typing import TypedDict, Annotated, Sequence, Literal
import operator
from langchain_core.messages import BaseMessage

import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import Graph, StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import  AIMessage, HumanMessage, ToolMessage

from langchain_community.tools.tavily_search import TavilySearchResults


load_dotenv(dotenv_path="../.env")

# Create the llm structure
# alternative models: "gpt-3.5-turbo", "gpt-4"
model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.5)

tool = TavilySearchResults(max_results=2)

tools = [tool]

llm_with_tools = model.bind_tools(tools)

class CustomState(TypedDict):
    messages: Annotated[list, add_messages]

def chatbot(state: CustomState):
    return { "messages": [llm_with_tools.invoke(state["messages"])] }

graph_builder = StateGraph(CustomState)
graph_builder.add_node("chatbot", chatbot)    

class BasicToolNode:
    def __init__(self, tools: list) -> None:
        self.tools_by_name = {tool.name: tool for tool in tools}

    def __call__(self, inputs: dict):
        if messages := inputs.get("messages", []):
            message = messages[-1]
        else:
            raise ValueError("No messages found in inputs")

        outputs = []
        for tool_call in message.tool_calls:

            tool = self.tools_by_name[tool_call["name"]]
            tool_result = tool.invoke(tool_call["args"]) 
            outputs.append(ToolMessage(content=json.dumps(tool_result), name=tool_call["name"], tool_call_id=tool_call["id"]))

        return {"messages": outputs}

tool_node = BasicToolNode(tools=[tool])
graph_builder.add_node("tools", tool_node)

def route_tools(
        state: CustomState,
) -> Literal["tools", "__end__"]:
    """ Use in the conditional_edge to route to the ToolNode if the last message has tool calls. Otherwise, route to the end. """

    if isinstance(state, list):
        ai_message = state[-1]
    elif messages := state.get("messages", []):
        ai_message = messages[-1]
    else:
        raise ValueError(f"No messages found in input state to tool_edge: {state}")

    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        return "tools"
    return "__end__"

graph_builder.add_conditional_edges(
    "chatbot",
    route_tools,
    {"tools": "tools", "__end__": "__end__"}
)

graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")
graph = graph_builder.compile()

input = {"messages": [HumanMessage(content="Hello, what can you tell me about the LangGraph framework?")]}
response = graph.invoke(input)
print(response["messages"][-1].content)