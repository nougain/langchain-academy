# The LangGraph API supports breakpoints.
from langchain_core.messages import HumanMessage

from langgraph_sdk import get_client
client = get_client(url="http://localhost:8123")

#
# Breakpoints using LangGraph API
#
# We can add interrupt_before=["node"] when compiling the graph that is running in Studio.
# However, with the API, you can also pass interrupt_before to the stream method directly.
#
async def UsingAPI():
    #await print(client.assistants.get("3-agent"))
    initial_input = {"messages": HumanMessage(content="Multiply 2 and 3")}
    agent_id = "3-agent"

    thread = await client.threads.create()

    async for chunk in client.runs.stream(
        thread["thread_id"],
        assistant_id=agent_id,
        input=initial_input,
        stream_mode="values",
        interrupt_before=["tools"],         #<-- NOTE interrupt_before
    ):
        print(f"Receiving new event of type: {chunk.event}...")
        messages = chunk.data.get('messages', [])
        if messages:
            print(messages[-1])
        print("-" * 50)


    # INTERRUPTED
    # We can get the state and look at the next node to call.
    # This is a nice way to see that the graph has been interrupted.
    #TBD# state = client.assistants.get(agent_id).get_state(thread)
    #TBD# print(state.next)


    # Get user feedback
    user_approval = input("Do you want to call the tool? (yes/no): ")


    print("::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")

    # Check approval
    if user_approval.lower() == "yes":
        # RESUME
        # Now, we can proceed from the breakpoint just like we did before by passing the thread_id and None as the input!
        async for chunk in client.runs.stream(
            thread["thread_id"],
            agent_id,
            input=None,
            stream_mode="values",
            interrupt_before=["tools"],
        ):
            print(f"Receiving new event of type: {chunk.event}...")
            messages = chunk.data.get('messages', [])
            if messages:
                print(messages[-1])
            print("-" * 50)

import asyncio
asyncio.run(UsingAPI())