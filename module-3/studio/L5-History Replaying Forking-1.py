#
# Now, let's see how LangGraph supports debugging by viewing, re-playing, and even forking from past states.
#
from langchain_openai import ChatOpenAI


# ....................................
# LLM with Tools
# ....................................
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
llm = ChatOpenAI(model="gpt-4o", temperature=0, max_tokens=30)
llm_with_tools = llm.bind_tools(tools)


# ....................................
# Graph (Classic React Agent)
# ....................................
from IPython.display import Image, display
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import MessagesState
from langgraph.graph import START, END, StateGraph
from langgraph.prebuilt import tools_condition, ToolNode
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

# System message
sys_msg = SystemMessage(content="You are a helpful assistant tasked with performing arithmetic on a set of inputs.")

# Node
def assistant(state: MessagesState):
   return {"messages": [llm_with_tools.invoke([sys_msg] + state["messages"])]}

# Graph
builder = StateGraph(MessagesState)
# Define nodes: these do the work
builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode(tools))
# Define edges: these determine the control flow
builder.add_edge(START, "assistant")
builder.add_conditional_edges(
    "assistant",
    # If the latest message (result) from assistant is a tool call -> tools_condition routes to tools
    # If the latest message (result) from assistant is a not a tool call -> tools_condition routes to END
    tools_condition,
)
builder.add_edge("tools", "assistant")

memory = MemorySaver()
graph = builder.compile(checkpointer=MemorySaver())

# Show
#display(Image(graph.get_graph(xray=True).draw_mermaid_png()))

# ....................................
# Run it
# ....................................
# Input
initial_input = {"messages": HumanMessage(content="Multiply 2 and 3")}

# Config/Thread
config = {"configurable": {"thread_id": "1"}, "tags": ["RCNTag-History!1"], "metadata": {"RCNKey1":"History1"}}

# Run the graph until the first interruption
for event in graph.stream(initial_input, config, stream_mode="values"):
    event['messages'][-1].pretty_print()


###########################################################################################

print("\n##### Graph State ###################################################")
# ....................................
# Graph State
# ....................................
result = graph.get_state({'configurable': {'thread_id': '1'}})
print("graph.get_state:: " +str(result))

print("\n##### History ###################################################")
# ....................................
# Browse History
# ....................................
all_states = [s for s in graph.get_state_history(config)]
states_len = len(all_states)
print("states_len:: " +str(states_len))
print("\nall_states[0]:: " +str(all_states[0]))         # Current State
print("\nall_states[-1]:: " +str(all_states[-1]))       # First state __START__
print("\nall_states[-2]:: " +str(all_states[-2]))       # HumanMessage(content='Multiply 2 and 3'...

print("\n##### Replay ###################################################")
# ....................................
# Replay
# ....................................
to_replay = all_states[-2]              # The step that received human input!
print("\nto_replay:: " +str(to_replay))
print("\nto_replay.values:: " +str(to_replay.values))
print("\ntto_replay.next:: " +str(to_replay.next))
print("\nto_replay.config:: " +str(to_replay.config))
# Replay (not execute) from the Human Step. To replay from here, we simply pass the config back to the agent!
# The graph knows that this checkpoint has already been executed. It just re-plays from this checkpoint!
to_replay.config.update({"tags": ["RCNTag-Replay!1"], "metadata": {"RCNKey1":"Replay1"}})
for event in graph.stream(None, to_replay.config, stream_mode="values"):
    event['messages'][-1].pretty_print()

print("\n##### Forking ###################################################")
# ....................................
# Forking (Re-executing)
# ....................................
all_states = [s for s in graph.get_state_history(config)]
states_len = len(all_states)
print("states_len (before forking):: " +str(states_len))
#
to_fork = all_states[-2]
print("\nto_fork.values[\"messages\"]:: " +str(to_fork.values["messages"]))
print("\nto_fork.config (before forking):: " +str(to_fork.config))
# Let's modify the state at this checkpoint. We can just run update_state with the checkpoint_id supplied.
# Remember how our reducer on messages works:
#  - It will append, unless we supply a message ID.
#  - We supply the message ID to overwrite the message, rather than appending to state!
# So, to overwrite the message, we just supply the message ID, which we have to_fork.values["messages"].id.
#
to_fork.config.update({"tags": ["RCNTag-UpdateState!1"], "metadata": {"RCNKey1":"UpdateState1"}})
fork_config = graph.update_state(
    to_fork.config,
    {"messages": [HumanMessage(content='Multiply 5 and 3', id=to_fork.values["messages"][0].id)]},
)
print("\nfork_config (after update_state. checkout the new checkpoint_id):: " +str(fork_config))
# This creates a new, forked checkpoint. But, the metadata - e.g., where to go next - is preserved!
# We can see the current state of our agent has been updated with our fork.
#
all_states = [s for s in graph.get_state_history(config)]
msg = all_states[0].values["messages"]
print("\nmsg (after update_state):: " +str(msg))       # You will see id is same but the content has been modified
states_len = len(all_states)
print("\nstates_len (after update_state):: " +str(states_len))
#
st = graph.get_state({'configurable': {'thread_id': '1'}})
print("\ncurrent state (before fork execution):: " +str(st))

# Now, when we stream, the graph knows this checkpoint has never been executed.
# So, the graph runs, rather than simply re-playing.
#########################################################
fork_config.update({"tags": ["RCNTag-Forked!1"], "metadata": {"RCNKey1":"Forked1"}})
for event in graph.stream(None, fork_config, stream_mode="values"):
    event['messages'][-1].pretty_print()
#########################################################

all_states = [s for s in graph.get_state_history(config)]
states_len = len(all_states)
print("\nstates_len (after fork execution):: " +str(states_len))
#
st = graph.get_state({'configurable': {'thread_id': '1'}})
print("\ncurrent state (after fork execution):: " +str(st))
