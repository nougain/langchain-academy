# ------------------------------------------------------------------------------------------------------
# Chatbot with EXTERNAL memory (using free SQLite)
#
# - pip install -U langgraph-checkpoint-sqlite
# - Download Precompiled Binaries for Windows (64-bit DLL (x64) for SQLite version 3.47.0): https://www.sqlite.org/download.html
# - Place unzipped folder having sqlite3.dll and sqlite3.def in the path
# ------------------------------------------------------------------------------------------------------

###
### LLM MODEL ###
###
from langchain_openai import ChatOpenAI
model = ChatOpenAI(model="gpt-4o",temperature=0, max_tokens=30)


###
### STATE ###
###
from langgraph.graph import MessagesState       #Has in-built 'messages' key
class State(MessagesState):
    summary: str                                #Additional channel / field


###
### LLM Call ###
###
# Define the logic to call the model
from langchain_core.messages import SystemMessage, HumanMessage, RemoveMessage
def call_model(state: State):
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

    response = model.invoke(messages, {"tags": ["RCNTag-Chatbot!1"], "metadata": {"RCNKey1":len(messages)}})
    return {"messages": response}


###
### Summarization ###
###
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
    response = model.invoke(messages, {"tags": ["RCNTag-Chatbot!2"], "metadata": {"RCNKey1":len(messages)}})

    # Delete all but the 2 most recent messages
    delete_messages = [RemoveMessage(id=m.id) for m in state["messages"][:-2]]
    return {"summary": response.content, "messages": delete_messages}


###
### Next Node ###
###
from langgraph.graph import END
# Determine whether to end or summarize the conversation i.e. which node to go to
def should_continue(state: State):
    """Return the next node to execute."""

    # Messages
    messages = state["messages"]

    # If there are more than six messages, then we summarize the conversation
    print("Number of messages in the conversation: " +str(len(messages)))
    if len(messages) > 6:
        print("----------->beep-beep-beep-beep Returning the \"summarize_conversation\" node...")
        return "summarize_conversation"

    # Otherwise we can just end
    return END


####################################################################################
import sqlite3
#
# If we supply ":memory:" it creates an in-memory Sqlite database.
#
conn = sqlite3.connect(":memory:", check_same_thread = False)

#
# But, if we supply a db path, then it will create a database for us!
#
# pull file if it doesn't exist and connect to local db
# !mkdir -p state_db && [ ! -f state_db/example.db ] && wget -P state_db https://github.com/langchain-ai/langchain-academy/raw/main/module-2/state_db/example.db
#
db_path = "state_db\\example.db"
db_path = "D:\\Work\\RPA\\15-Langchain\\langchain-academy\\module-2\\state_db\\example.db"
conn = sqlite3.connect(db_path, check_same_thread=False)


#
# Here is our checkpointer
#
from langgraph.checkpoint.sqlite import SqliteSaver
memory_sqlite = SqliteSaver(conn)
####################################################################################



###
### Graph with Memory ###
###
from IPython.display import Image, display
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START

# Define a new graph
workflow = StateGraph(State)
workflow.add_node("conversation", call_model)
workflow.add_node("summarize_conversation", summarize_conversation)

# Set the entrypoint as conversation
workflow.add_edge(START, "conversation")
workflow.add_conditional_edges("conversation", should_continue)
workflow.add_edge("summarize_conversation", END)

# Compile (with Memory)
# memory = MemorySaver()
# graph = workflow.compile(checkpointer=memory)
graph = workflow.compile(checkpointer=memory_sqlite)
#display(Image(graph.get_graph().draw_mermaid_png()))

# Create a thread

# Start conversation
print("................................Conversation-1...................................................")
input_message = HumanMessage(content="hi! I'm Ramesh")
config = {"configurable": {"thread_id": "1"}, "tags": ["RCNTag-Chatbot!3"], "metadata": {"RCNKey1":"Conv1"}}
output = graph.invoke({"messages": [input_message]}, config)
for m in output['messages'][-1:]:
    m.pretty_print()
brief = graph.get_state(config).values.get("summary","")
print("SUMMARY: " + brief)

print("................................Conversation-2...................................................")
input_message = HumanMessage(content="what's my name?")
config = {"configurable": {"thread_id": "1"}, "tags": ["RCNTag-Chatbot!4"], "metadata": {"RCNKey1":"Conv2"}}
output = graph.invoke({"messages": [input_message]}, config)
for m in output['messages'][-1:]:
    m.pretty_print()
brief = graph.get_state(config).values.get("summary","")
print("SUMMARY: " + brief)

print("................................Conversation-3...................................................")
input_message = HumanMessage(content="I like the man made ancient wonders!")
config = {"configurable": {"thread_id": "1"}, "tags": ["RCNTag-Chatbot!5"], "metadata": {"RCNKey1":"Conv3"}}
output = graph.invoke({"messages": [input_message]}, config)
for m in output['messages'][-1:]:
    m.pretty_print()
brief = graph.get_state(config).values.get("summary","")
print("SUMMARY: " + brief)

print("................................Conversation-4...................................................")
input_message = HumanMessage(content="Tell me about the pyramid of khufru!")
config = {"configurable": {"thread_id": "1"}, "tags": ["RCNTag-Chatbot!6"], "metadata": {"RCNKey1":"Conv4"}}
output = graph.invoke({"messages": [input_message]}, config)
for m in output['messages'][-1:]:
    m.pretty_print()
brief = graph.get_state(config).values.get("summary","")
print("SUMMARY: " + brief)

print("................................Conversation-5...................................................")
input_message = HumanMessage(content="Is it the largest one?")
config = {"configurable": {"thread_id": "1"}, "tags": ["RCNTag-Chatbot!7"], "metadata": {"RCNKey1":"Conv5"}}
output = graph.invoke({"messages": [input_message]}, config)
for m in output['messages'][-1:]:
    m.pretty_print()
brief = graph.get_state(config).values.get("summary","")
print("SUMMARY: " + brief)