#########################################
# STREAMING TOKENS
#########################################
from IPython.display import Image, display

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, RemoveMessage
from langchain_core.runnables import RunnableConfig

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.graph import MessagesState

# LLM
model = ChatOpenAI(model="gpt-4o", temperature=0, max_tokens=30)

# State
class State(MessagesState):
    summary: str

# Define the logic to call the model
# ---------------------------------------------------
def call_model(state: State, config: RunnableConfig):
    # Get summary if it exists
    summary = state.get("summary", "")

    # If there is summary, then we add it
    if summary:
        # Add summary to system message
        system_message = f"Summary of conversation earlier: {summary}"
        # Append summary to any newer messages
        messages = [SystemMessage(content=system_message)] + state["messages"]
    else:
        messages = state["messages"]

    response = model.invoke(messages, config)
    return {"messages": response}

# Summarize
# ---------------------------------------------------
def summarize_conversation(state: State):
    # First, we get any existing summary
    summary = state.get("summary", "")

    # Create our summarization prompt
    if summary:
        # A summary already exists
        summary_message = (
            f"This is summary of the conversation to date: {summary}\n\n"
            "Extend the summary by taking into account the new messages above:"
        )
    else:
        summary_message = "Create a summary of the conversation above:"

    # Add prompt to our history
    messages = state["messages"] + [HumanMessage(content=summary_message)]
    response = model.invoke(messages)

    # Delete all but the 2 most recent messages
    delete_messages = [RemoveMessage(id=m.id) for m in state["messages"][:-2]]
    return {"summary": response.content, "messages": delete_messages}

# Determine whether to end or summarize the conversation
# ---------------------------------------------------
def should_continue(state: State):
    """Return the next node to execute."""

    messages = state["messages"]

    # If there are more than six messages, then we summarize the conversation
    if len(messages) > 6:
        return "summarize_conversation"

    # Otherwise we can just end
    return END


# Define a new graph
workflow = StateGraph(State)
workflow.add_node("conversation", call_model)
workflow.add_node(summarize_conversation)

# Set the entrypoint as conversation
workflow.add_edge(START, "conversation")
workflow.add_conditional_edges("conversation", should_continue)
workflow.add_edge("summarize_conversation", END)

# Compile
memory = MemorySaver()
graph = workflow.compile(checkpointer=memory)
#display(Image(graph.get_graph().draw_mermaid_png()))

##############################################################################################################
print("\nXXXXXXXX-Tokens-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX\n")

import asyncio
import nest_asyncio

async def stream_tokens():
    config = {"configurable": {"thread_id": "1"}, "tags": ["RCNTag-StreamingToken!1"], "metadata": {"RCNKey1":"StreamingToken!1"}}
    input_message = HumanMessage(content="Tell me about the great pyramid of giza")
    result = graph.astream_events({"messages": [input_message]}, config, version="v2")
    async for event in result:
        print(f"Node: {event['metadata'].get('langgraph_node','')}. "
              f"Type: {event['event']}. "
              f"Name: {event['name']}")

    print("\n------------------------------------------------------------------------------------------------------\n")
    node_to_stream = 'conversation'
    config = {"configurable": {"thread_id": "2"}, "tags": ["RCNTag-StreamingToken!2"], "metadata": {"RCNKey1":"StreamingToken!2"}}
    result = graph.astream_events({"messages": [input_message]}, config, version="v2")
    async for event in result:
        # Get chat model tokens from a particular node
        if event["event"] == "on_chat_model_stream" and event['metadata'].get('langgraph_node','') == node_to_stream:
            print(event["data"])

    print("\n------------------------------------------------------------------------------------------------------\n")
    node_to_stream = 'conversation'
    config = {"configurable": {"thread_id": "3"}, "tags": ["RCNTag-StreamingToken!3"], "metadata": {"RCNKey1":"StreamingToken!3"}}
    result = graph.astream_events({"messages": [input_message]}, config, version="v2")
    async for event in result:
        # Get chat model tokens from a particular node
        if event["event"] == "on_chat_model_stream" and event['metadata'].get('langgraph_node','') == node_to_stream:
            print(event["data"]["chunk"].content, end=" | ")

import asyncio
asyncio.run(stream_tokens())