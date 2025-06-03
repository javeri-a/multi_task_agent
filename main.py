
import os
import asyncio
from dotenv import load_dotenv
import chainlit as cl
from datetime import datetime

from agents import (
    AsyncOpenAI,
    OpenAIChatCompletionsModel,
    Agent,
    Runner,
    RunConfig,
)


load_dotenv()

# =================== AGENT RESPONSE FUNCTION ====================
async def generate_response(task: str, model_name: str, api_key: str) -> str:
    """Creates and runs an agent to respond to a specific task."""
    external_client = AsyncOpenAI(
        api_key=api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )

    model = OpenAIChatCompletionsModel(
        model=model_name,
        openai_client=external_client
    )

    config = RunConfig(
        model=model,
        model_provider=external_client,
        tracing_disabled=True
    )

    assistant = Agent(
        name="Assistant",
        instructions=f"You are assigned to complete this task: {task}"
    )

    result = await Runner.run(assistant, task, run_config=config)
    return result.final_output


class Manager:
    

    def __init__(self, model_name: str, api_key: str):
        self.model_name = model_name
        self.api_key = api_key

    async def delegate_task(self, task: str) -> str:
        task_lower = task.lower()

   
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] Manager received task: {task}")

        if "website" in task_lower or "web" in task_lower:
            return await generate_response(f"Web Developer Task: {task}", self.model_name, self.api_key)

        elif "market" in task_lower or "ads" in task_lower:
            return await generate_response(f"Marketing Task: {task}", self.model_name, self.api_key)

        elif "design" in task_lower or "graphic" in task_lower:
            return await generate_response(f"Graphic Design Task: {task}", self.model_name, self.api_key)

        else:
            return "⚠️ Manager: Sorry, I couldn't categorize this task. Please specify if it's Web, Marketing, or Design."


@cl.on_message
async def handle_user_input(message: cl.Message):

    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    MODEL_NAME = "gemini-2.0-flash"

    manager = Manager(MODEL_NAME, GEMINI_API_KEY)

    task = message.content.strip()

    await cl.Message(content="⏳ Processing your task, please wait...").send()

    try:
        response = await manager.delegate_task(task)
        await cl.Message(content=f"✅ Task Completed:\n\n{response}").send()

    except Exception as e:
        await cl.Message(content=f"❌ Error: {str(e)}").send()


if __name__ == "__main__":
    async def test_manager():
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        MODEL_NAME = "gemini-2.0-flash"
        manager = Manager(MODEL_NAME, GEMINI_API_KEY)

        test_tasks = [
            "Build a responsive website landing page.",
            "Create a marketing strategy for social media ads.",
            "Design a modern logo for a new brand.",
            "Write a business plan."
        ]

        for task in test_tasks:
            print(f"\n🧾 Task: {task}")
            result = await manager.delegate_task(task)
            print(f"🎯 Result:\n{result}")

    asyncio.run(test_manager())
