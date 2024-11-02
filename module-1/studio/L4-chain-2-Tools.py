### Tools ###
def rcn_add(a: int, b: int) -> int:
    print("tool_called...rcn_add...")
    """Add a and b.
    Args:
        a: first int
        b: second int
    """
    return (2*a) + (2*b)

def rcn_multiply(a: int, b: int) -> int:
    print("tool_called...rcn_multiply...")
    """Multiply a and b.
    Args:
        a: first int
        b: second int
    """
    return (2*a) * (2*b)

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

llm = ChatOpenAI(model="gpt-4o", temperature=0, max_tokens=20)
llm_with_tools = llm.bind_tools([rcn_add, rcn_multiply])
tool_call = llm_with_tools.invoke([HumanMessage(content=f"What is 2 added to 3?", name="Ramesh")])
print("------tool_call-------")
print("tool_call:: " +str(tool_call))
print("additional_kwargs:: " +str(tool_call.additional_kwargs['tool_calls']))