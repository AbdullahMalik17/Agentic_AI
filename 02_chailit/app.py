import chainlit as cl

@cl.on_message
async def main(message: cl.Message):
    # Our custom logic goes here...
    # Send a fake response back to the user
    await cl.Message(
        content=f"Received  Assalam o Alaikum ! . Which type f information do you want to get : {message.content}",
    ).send()