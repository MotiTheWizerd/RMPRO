import os
import uuid
from dotenv import load_dotenv

from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.runners import Runner
from agents.alpha.get_alpha import get_alpha
from agents.utils.llm.call_agent_async import call_agent_async
from agents.utils.sessions.get_session import get_session
load_dotenv()




async def main():
   
    APP_NAME="test-agent"
    SESSION_ID = str(uuid.uuid4())
    USER_ID = "user-1"

    state= {
        "current_speaker" : "Moti"
    }
    session_service, session = await get_session(app_name=APP_NAME,session_id=SESSION_ID,user_id=USER_ID,state=state)
    agent = get_alpha() 
   
    runner = Runner(app_name=APP_NAME, agent=agent, session_service=session_service)
    while True:
        # Small matrix effect before each prompt (very brief)
        # matrix_effect(0.3)
        is_session_debug = False
        if is_session_debug:
            # Print session state for debugging
            print("--- Session State for User ID:", USER_ID, "Session ID:", SESSION_ID, "---")
            print("user_request:", session.state["user_request"])
            print("task_for_powershell_script_writer:", session.state["task_for_powershell_script_writer"])
        user_input = input("Say something: ")
        session.state["user_request"] = user_input
        if user_input.lower() == "exit":
            # Exit sequence
            break
        else:
            # Process the message
            response = await call_agent_async(
                runner=runner,
                user_id=USER_ID, 
                session_id=SESSION_ID, 
                message=user_input
            )

        # ✨ pull the updated state AFTER the run
        session = await session_service.get_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=SESSION_ID,
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
