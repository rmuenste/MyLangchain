import getpass
import os
import datetime
import gradio as gr
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, trim_messages
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from operator import itemgetter

load_dotenv(dotenv_path="../.env")

store = {}

def get_session_history(session_id) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]    

#=============================================================================
# Build the main components for the chatbot
#=============================================================================

prompt = ChatPromptTemplate.from_messages([
    SystemMessage(content="You are a helpful assistant."),
    MessagesPlaceholder(variable_name="messages"),
])

# Create the llm structure
model = ChatOpenAI(model="gpt-3.5-turbo")
#model = ChatOpenAI(model="gpt-4")

## Create a trimmer for the messages
trimmer = trim_messages(
    max_tokens=256,
    strategy="last",
    token_counter=model,
    include_system=True,
    allow_partial=False,
    start_on="human"
)

## Create the chain
#print(itemgetter("messages"))
#rpt = RunnablePassthrough.assign(messages = {"messages": itemgetter("messages")})
#chain = (
#    trimmer
#    | prompt 
#    | model
#)

#print(messages=itemgetter("messages") | trimmer)
#msg = trimmer.invoke({"messages": itemgetter("messages")})


# Add a history and a session id to the model
# Simple variant
#model_with_history = RunnableWithMessageHistory(model, get_session_history)
#config = {"configurable": {"session_id" : "abc2"}}

#chain = prompt | model
chain = trimmer | prompt | model

# Variant with managed history and a chain 
model_with_history = RunnableWithMessageHistory(
    chain, 
    get_session_history,
    input_messages_key="messages"
    )
config = {"configurable": {"session_id" : "abc2"}}

# Variant without history class
#model.invoke([
#    SystemMessage(content="You are a helpful assistant."),
#    HumanMessage(content="Hi! I am Robert"),
#    AIMessage(content="Hi Robert! How can I help you today?")
#    ]
#    )

# Variant with managed history class
response = model_with_history.invoke(
    {"messages": [HumanMessage(content="Hi! I am Robert")]},
    config=config
)

print(response)

response = model_with_history.invoke(
    {"messages": [HumanMessage(content="I implemented a chat interface with a managed history. This is we you should have my name in memory. So what is my name?")]},
    config=config
)


print(response)