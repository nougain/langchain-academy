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

    response = model.invoke(messages, {"tags": ["RCNTag-Chatbot."], "metadata": {"RCNKey1":len(messages)}})
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
    response = model.invoke(messages, {"tags": ["RCNTag-Chatbot.."], "metadata": {"RCNKey1":len(messages)}})

    # Delete all but the 2 most recent messages
    delete_messages = [RemoveMessage(id=m.id) for m in state["messages"][:-2]]
    return {"summary": response.content, "messages": delete_messages}


###
### Next Node ###
###
from langgraph.graph import END
# Determine whether to end or summarize the conversation
def should_continue(state: State):
    """Return the next node to execute."""

    # Messages
    messages = state["messages"]

    # If there are more than six messages, then we summarize the conversation
    print("Number of messages in the conversation: " +str(len(messages)))
    if len(messages) > 6:
        return "summarize_conversation"

    # Otherwise we can just end
    return END


###
### Graph with Memory ###
###
from IPython.display import Image, display
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START

# Define a new graph
workflow = StateGraph(State)
workflow.add_node("conversation", call_model)
workflow.add_node(summarize_conversation)

# Set the entrypoint as conversation
workflow.add_edge(START, "conversation")
workflow.add_conditional_edges("conversation", should_continue)
workflow.add_edge("summarize_conversation", END)

# Compile (with Memory)
memory = MemorySaver()
graph = workflow.compile(checkpointer=memory)
#display(Image(graph.get_graph().draw_mermaid_png()))

# Create a thread

# Start conversation
print("................................Conversation-1...................................................")
input_message = HumanMessage(content="hi! I'm Ramesh")
config = {"configurable": {"thread_id": "1"}, "tags": ["RCNTag-Chatbot..."], "metadata": {"RCNKey1":"Conv1"}}
output = graph.invoke({"messages": [input_message]}, config)
for m in output['messages'][-1:]:
    m.pretty_print()

print("................................Conversation-2...................................................")
input_message = HumanMessage(content="what's my name?")
config = {"configurable": {"thread_id": "1"}, "tags": ["RCNTag-Chatbot...."], "metadata": {"RCNKey1":"Conv2"}}
output = graph.invoke({"messages": [input_message]}, config)
for m in output['messages'][-1:]:
    m.pretty_print()

print("................................Conversation-3...................................................")
input_message = HumanMessage(content="i like the 49ers!")
config = {"configurable": {"thread_id": "1"}, "tags": ["RCNTag-Chatbot....."], "metadata": {"RCNKey1":"Conv3"}}
output = graph.invoke({"messages": [input_message]}, config)
for m in output['messages'][-1:]:
    m.pretty_print()
