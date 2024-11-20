#
# History. Replay. Fork.
# Debugging.
# Using Langgraph Server API
#

from langchain_core.messages import HumanMessage
from langgraph_sdk import get_client

# Deployed graphs URL
client = get_client(url="http://localhost:8123")

#
#
#
async def UsingAPI():
    # Input Message
    initial_input = {"messages": HumanMessage(content="Multiply 2 and 3")}

    # Agent ID (deployed)
    agent_id = "3-agent"

    # Thread
    thread = await client.threads.create()

    async for chunk in client.runs.stream(
        thread["thread_id"],
        assistant_id=agent_id,
        input=initial_input,
        stream_mode="updates",
    ):
        if chunk.data:
            assisant_node = chunk.data.get('assistant', {}).get('messages', [])
            tool_node = chunk.data.get('tools', {}).get('messages', [])
            if assisant_node:
                print("-" * 20 + "Assistant Node" + "-" * 20)
                print(assisant_node[-1])
            elif tool_node:
                print("-" * 20 + "Tools Node" + "-" * 20)
                print(tool_node[-1])
            else:
                print("-" * 20 + "????? Node" + "-" * 20)
                print(chunk.data)

    current_state = await client.threads.get_state(thread['thread_id'])
    print("\ncurrent_state['next']: " +str(current_state['next']))

    # ....................................
    # Replay
    # ....................................
    # Now, let's look at replaying from a specified checkpoint.
    # We simply need to pass the checkpoint_id.
    states = await client.threads.get_history(thread['thread_id'])
    to_replay = states[-2]
    print("to_replay:: " +str(to_replay))
    print("\n"+"o"*60)

    # Let's stream with stream_mode="values" to see the full state at every node as we replay.
    async for chunk in client.runs.stream(
            thread["thread_id"],
            assistant_id=agent_id,
            input=None,
            stream_mode="values",
            checkpoint_id=to_replay['checkpoint_id']            #Note 'checkpoint_id'
    ):
        print(f"Receiving new event of type: {chunk.event}...")
        print(chunk.data)
        print("~~~~~~~~~~~~")

    #
    # We can all view this as streaming only "updates" to state made by the nodes that we reply.
    #
    print("o" * 20 + "Streaming Updates Only" + "o" * 20)
    async for chunk in client.runs.stream(
        thread["thread_id"],
        assistant_id=agent_id,
        input=None,
        stream_mode="updates",
        checkpoint_id=to_replay['checkpoint_id']            #Note 'checkpoint_id'
    ):
        if chunk.data:
            assisant_node = chunk.data.get('assistant', {}).get('messages', [])
            tool_node = chunk.data.get('tools', {}).get('messages', [])
            if assisant_node:
                print("-" * 20+"Assistant Node"+"-" * 20)
                print(assisant_node[-1])
            elif tool_node:
                print("-" * 20+"Tools Node"+"-" * 20)
                print(tool_node[-1])

    # ....................................
    # Forking
    # ....................................
    # Let's get the same step as we worked with above, the human input.
    # Let's create a new thread with out agent.
    initial_input = {"messages": HumanMessage(content="Multiply 2 and 3")}
    thread = await client.threads.create()
    async for chunk in client.runs.stream(
            thread["thread_id"],
            assistant_id=agent_id,
            input=initial_input,
            stream_mode="updates",
    ):
        if chunk.data:
            assisant_node = chunk.data.get('assistant', {}).get('messages', [])
            tool_node = chunk.data.get('tools', {}).get('messages', [])
            if assisant_node:
                print("-" * 20 + "Assistant Node" + "-" * 20)
                print(assisant_node[-1])
            elif tool_node:
                print("-" * 20 + "Tools Node" + "-" * 20)
                print(tool_node[-1])

    states = await client.threads.get_history(thread['thread_id'])
    to_fork = states[-2]
    print("")
    print("to_fork['values']:: " +str(to_fork['values']))
    print("to_fork['values']['messages'][0]['id']:: " + str(to_fork['values']['messages'][0]['id']))
    print("to_fork['next']:: " + str(to_fork['next']))
    print("to_fork['checkpoint_id']:: " + str(to_fork['checkpoint_id']))

    #
    # Let's edit the state
    #
    # Remember how our reducer on messages works:
    #   - It will append, unless we supply a message ID.
    #   - We supply the message ID to overwrite the message, rather than appending to state!
    #
    forked_input = {"messages": HumanMessage(content="Multiply 3 and 3",
                                             id=to_fork['values']['messages'][0]['id'])}

    forked_config = await client.threads.update_state(
        thread["thread_id"],
        forked_input,
        checkpoint_id=to_fork['checkpoint_id']
    )
    print("")
    print("forked_config:: " +str(forked_config))

    states = await client.threads.get_history(thread['thread_id'])
    print("edited states[0]:: " +str(states[0]))

    #
    # To rerun, we pass in the checkpoint_id
    #
    print("")
    print("*" * 60)
    print("Rerun (fork execution):: ")
    print("*"*60)
    async for chunk in client.runs.stream(
            thread["thread_id"],
            assistant_id=agent_id,
            input=None,
            stream_mode="updates",
            checkpoint_id=forked_config['checkpoint_id']
    ):
        if chunk.data:
            assisant_node = chunk.data.get('assistant', {}).get('messages', [])
            tool_node = chunk.data.get('tools', {}).get('messages', [])
            if assisant_node:
                print("-" * 20 + "Assistant Node" + "-" * 20)
                print(assisant_node[-1])
            elif tool_node:
                print("-" * 20 + "Tools Node" + "-" * 20)
                print(tool_node[-1])

import asyncio
asyncio.run(UsingAPI())