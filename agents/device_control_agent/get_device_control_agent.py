from google.adk.agents.llm_agent import LlmAgent
from agents.device_control_agent.prompts.get_prompt import get_device_control_prompt
from agents.tools.execute_ir_command_tool import execute_ir_command

def get_device_control_agent():
    return LlmAgent(
        name="device_control_agent",
        model="gemini-2.0-flash", 
        instruction=get_device_control_prompt(),
        description="calling a tool that control home devices",
        tools=[execute_ir_command]
    )
