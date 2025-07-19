
from google.adk.sessions import InMemorySessionService

async def get_session(app_name: str, session_id: str, user_id: str, state=None):
    if state is None:
        state = {
            "user_request": "",
        }
    print("state", state)
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name=app_name,
        session_id=session_id,
        user_id=user_id,
        state=state
    )
    return session_service, session