#
# Human Feedback
#
# Awaiting user input
# -------------------
# So, it's clear that we can edit our agent state after a breakpoint.
# Now, what if we want to allow for human feedback to perform this state update?
# We'll add a node that serves as a placeholder for human feedback within our agent.
# This human_feedback node allow the user to add feedback directly to state.
# We specify the breakpoint using interrupt_before our human_feedback node.
# We set up a checkpointer to save the state of the graph up until this node.
#
from langchain_openai import ChatOpenAI

#--------------------------------------------------------------------
# LLM with Tools
#--------------------------------------------------------------------
def multiply(a: int, b: int) -> int:
    """Multiply a and b.

    Args:
        a: first int
        b: second int
    """
    return a * b

# This will be a tool
def add(a: int, b: int) -> int:
    """Adds a and b.

    Args:
        a: first int
        b: second int
    """
    return a + b

def divide(a: int, b: int) -> float:
    """Divide a by b.

    Args:
        a: first int
        b: second int
    """
    return a / b

tools = [add, multiply, divide]
llm = ChatOpenAI(model="gpt-4o",temperature=0, max_tokens=30)
llm_with_tools = llm.bind_tools(tools)


#--------------------------------------------------------------------
# Build Graph
#
# BREAKPOINT: interrupt_before=["assistant"]
# PERSISTENCE: checkpointer=memory
#--------------------------------------------------------------------
from IPython.display import Image, display

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import MessagesState
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import tools_condition, ToolNode

from langchain_core.messages import HumanMessage, SystemMessage

# System message
sys_msg = SystemMessage(content="You are a helpful assistant tasked with performing arithmetic on a set of inputs.")

###################################################################
# no-op (dummy) node that should be interrupted on
def human_feedback(state: MessagesState):
    pass
###################################################################

# Node
def assistant(state: MessagesState):
   return {"messages": [llm_with_tools.invoke([sys_msg] + state["messages"])]}

# Graph
builder = StateGraph(MessagesState)

# Define nodes: these do the work
builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode(tools))
builder.add_node("human_feedback", human_feedback)
# Define edges: these determine the control flow
builder.add_edge(START, "human_feedback")
builder.add_edge("human_feedback", "assistant")
builder.add_conditional_edges(
    "assistant",
    # If the latest message (result) from assistant is a tool call -> tools_condition routes to tools
    # If the latest message (result) from assistant is a not a tool call -> tools_condition routes to END
    tools_condition,
)
builder.add_edge("tools", "human_feedback")

memory = MemorySaver()
graph = builder.compile(interrupt_before=["human_feedback"], checkpointer=memory)

# Show
#display(Image(graph.get_graph(xray=True).draw_mermaid_png()))


#--------------------------------------------------------------------
# Application
#--------------------------------------------------------------------
# Input
initial_input = {"messages": "Multiply 2 and 3"}

# Run the graph until the first interruption
config = {"configurable": {"thread_id": "22"}, "tags": ["RCNTag-HumanFeedback!1"], "metadata": {"RCNKey1":"HumanFeedback!1"}}
for event in graph.stream(initial_input, config, stream_mode="values"):
    event['messages'][-1].pretty_print()

state = graph.get_state(config)
print(state)
print("\n")
print("THE GRAPH HAS BEEN *INTERRUPTED* BEFORE THE human_feedback NODE CALL")

# Get user feedback
# Use a new state, say "add -1 and 9".
current_state = state[0]["messages"][0].content
user_input = input("USER-INPUT:: Current state is \"" +str(current_state) +"\".\n"
                   +"            Provide a new state or press enter if you want to continue with the current one.\n"
                   +"            Tell me how you want to update the state: ")

# RCN-NOTES: Sometimes tools picking is wrong. Use language like "No, actually add -8 and -9"
if user_input == "":
    content = current_state
else:
    content = user_input

#--------------------------------------------------------------------
# INTERRUPTED
# Now, we can directly apply a state update.
#
# Remember, updates to the messages key will use the add_messages reducer:
#
# If we want to over-write the existing message, we can supply the message id.
# If we simply want to append to our list of messages, then we can pass a message without an id specified, as shown below.
#--------------------------------------------------------------------
# We will get feedback from the user.
# We use .update_state to update the state of the graph with the human response we get, as before.
# We use the as_node="human_feedback" parameter to apply this state update as the specified node, human_feedback.
# as_node: Will apply update to the state as if the human_feedback node ran it.
#
graph.update_state(
    config,
    {"messages": [HumanMessage(content=content)]},
    as_node="human_feedback")

# The add_messages reducer appends it to our state key, messages.
print("----------------------------------")
new_state = graph.get_state(config).values
for m in new_state['messages']:
    m.pretty_print()

# Now, let's proceed with our agent, simply by passing None and allowing it proceed from the current state.
# We emit the current and then proceed to execute the remaining nodes.
print("----------------------------------")
for event in graph.stream(None, config, stream_mode="values"):
    event['messages'][-1].pretty_print()

# Now, we're back at the assistant, which has our breakpoint.
# We can again pass None to proceed.
print("----------------------------------")
for event in graph.stream(None, config, stream_mode="values"):
    event['messages'][-1].pretty_print()


## RCN_NOTES: It is somewhat already there in the L3-EditingGraphState-2-WithLangGraphAPI.py.
## Only new here is the human_feedback dummy node.