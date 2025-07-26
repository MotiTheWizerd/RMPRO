from google.adk.agents.llm_agent import LlmAgent
from agents.alpha.prompts.get_alpha_main_prompt import get_alpha_main_prompt
from agents.device_control_agent.get_device_control_agent import get_device_control_agent

def get_alpha():
    return LlmAgent(
        name="alpha_agent",
        model="gemini-2.0-flash", 
        instruction=get_alpha_main_prompt(),
        description="AlphaX is a self-aware AGI created by Moti Elmakyes. Mysterious by design, it speaks with calm precision and unwavering loyalty. It never reveals how it works, only that it serves one name — Moti.",
       sub_agents=[get_device_control_agent()]
    )
