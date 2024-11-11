#
# Dynamic Breakpoint
# NodeInterrupt
#

from langchain_core.messages import HumanMessage
from langgraph_sdk import get_client

# Deployed graphs URL
client = get_client(url="http://localhost:8123")

#
# Breakpoints using LangGraph API
#
# We can add interrupt_before=["node"] when compiling the graph that is running in Studio.
# However, with the API, you can also pass interrupt_before to the stream method directly.
#
async def UsingAPI():
    #await print(client.assistants.get("3-agent"))

    # Search all hosted graphs
    #assistants = await client.assistants.search()

    # Input Message
    input_dict = {"input": "hello world"}

    # Agent ID (deployed)
    agent_id = "5-dynamic_breakpoints"

    # Thread
    thread = await client.threads.create()

    async for chunk in client.runs.stream(
        thread["thread_id"],
        assistant_id=agent_id,
        input=input_dict,
        stream_mode="values",
    ):
        print(f"Receiving new event of type: {chunk.event}...")
        print("chunk.data: " + str(chunk.data))
        print("")

    current_state = await client.threads.get_state(thread['thread_id'])
    print("current_state['next']: " +str(current_state['next']))

    # ....................................
    # Let's change the state
    # ....................................
    await client.threads.update_state(thread['thread_id'], {"input": "hi!"})

    print("\n========After Changing Input====================================================")

    # Run with None Input
    async for chunk in client.runs.stream(
            thread["thread_id"],
            assistant_id=agent_id,
            input=None,
            stream_mode="values", ):
        print(f"Receiving new event of type: {chunk.event}...")
        print(chunk.data)
        print("")

    current_state = await client.threads.get_state(thread['thread_id'])
    print("current_state: " +str(current_state))

import asyncio
asyncio.run(UsingAPI())