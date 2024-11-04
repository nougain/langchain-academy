from langgraph.errors import InvalidUpdateError
from typing_extensions import TypedDict
from IPython.display import Image, display
from langgraph.graph import StateGraph, START, END

class State(TypedDict):
    foo: int

def node_1(state):
    print("---Node 1---")
    return {"foo": state['foo'] + 1}

def node_2(state):
    print("---Node 2---")
    return {"foo": state['foo'] + 1}

def node_3(state):
    print("---Node 3---")
    return {"foo": state['foo'] + 1}

# Build graph
builder = StateGraph(State)
builder.add_node("node_1", node_1)
builder.add_node("node_2", node_2)
builder.add_node("node_3", node_3)

# Logic
builder.add_edge(START, "node_1")
builder.add_edge("node_1", "node_2")
builder.add_edge("node_1", "node_3")
builder.add_edge("node_2", END)
builder.add_edge("node_3", END)

# Add
graph = builder.compile()
try:
    result = graph.invoke({"foo" : 1})  # This will throw error at runtime:
                                        # langgraph.errors.InvalidUpdateError: At key 'foo': Can receive only one value
                                        # per step. Use an Annotated key to handle multiple values.
                                        # This is because node2 and node3 in parallel trying to overwrite the foo.
                                        # They both attempt to overwrite the state within the same step. This is
                                        # ambiguous for the graph! Which state should it keep?
    print(result)
except  InvalidUpdateError  as e:
    print(f"RCN_ERROR: InvalidUpdateError occurred: {e}")

# View
display(Image(graph.get_graph().draw_mermaid_png()))