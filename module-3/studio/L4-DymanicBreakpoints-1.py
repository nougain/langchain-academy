#
# Dynamic Breakpoint
# NodeInterrupt
#
from IPython.display import Image, display
from typing_extensions import TypedDict
from langgraph.checkpoint.memory import MemorySaver
from langgraph.errors import NodeInterrupt
from langgraph.graph import START, END, StateGraph


class State(TypedDict):
    input: str


def step_1(state: State) -> State:
    print("---Step 1---")
    return state


def step_2(state: State) -> State:
    # Let's optionally raise a NodeInterrupt if the length of the input is longer than 5 characters
    if len(state['input']) > 5:
        raise NodeInterrupt(f"Received input that is longer than 5 characters: {state['input']}")

    print("---Step 2---")
    return state


def step_3(state: State) -> State:
    print("---Step 3---")
    return state


builder = StateGraph(State)
builder.add_node("step_1", step_1)
builder.add_node("step_2", step_2)
builder.add_node("step_3", step_3)
builder.add_edge(START, "step_1")
builder.add_edge("step_1", "step_2")
builder.add_edge("step_2", "step_3")
builder.add_edge("step_3", END)

# Set up memory
memory = MemorySaver()

# Compile the graph with memory
graph = builder.compile(checkpointer=memory)

# View
#display(Image(graph.get_graph().draw_mermaid_png()))

########################################################################
# Application
########################################################################
initial_input = {"input": "hello world"}
thread_config = {"configurable": {"thread_id": "M3L3-1"}, "tags": ["RCNTag-DynamicBP!1"], "metadata": {"RCNKey1":"DynamicBP!1"}}

# Run the graph until the first interruption
print("-"*60)
for event in graph.stream(initial_input, thread_config, stream_mode="values"):
    print("event: " +str(event))

state = graph.get_state(thread_config)
print("-"*60)
print("state.next: " +str(state.next))                 # We are stuck at step_2 as string length is > 5 i.e. NodeInterrupt happening
print("state.tasks: " +str(state.tasks))               # We can see that the Interrupt is logged to state.

# We can try to resume the graph from the breakpoint.
# But, this just re-runs the same node!
# Unless state is changed we will be stuck here.
for event in graph.stream(None, thread_config, stream_mode="values"):
    print(event)
state = graph.get_state(thread_config)
print("-"*60)
print(state.next)                           # We are still at ('step_2',)

#
# Now, we can update state. And resume the flow.
# --------------------------------------------------
graph.update_state(
    thread_config,
    {"input": "hi"},
)
print("*"*60)
for event in graph.stream(None, thread_config, stream_mode="values"):
    print(event)