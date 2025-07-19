import time
import uuid
import asyncio
from rich.console import Console
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
from rich.text import Text
from rich.spinner import Spinner
from rich import box

# Initialize Rich console with settings for better text wrapping
console = Console(width=120, soft_wrap=True, highlight=False)

def create_event_layout():
    """
    Create a simple layout for organizing the display of agent events
    """
    layout = Layout()
    layout.split(
        Layout(name="header", size=1),
        Layout(name="content")
    )
    return layout

async def process_event_content(event, part, is_final=False):
    """
    Process different types of content parts and return appropriate Rich renderable
    with special formatting for different content types
    
    Args:
        event: The event object
        part: The content part to process
        is_final: Whether this is the final response
        
    Returns:
        Rich renderable object for the content
    """
    
    if hasattr(part, "text") and part.text:
        display_text = part.text
        if len(display_text) > 1000 and not is_final:
            display_text = display_text[:1000] + "... [truncated]"
        
        # For final responses, use a special style with emoji
        if is_final:
            return Text("✅ " + display_text)
        # For regular text, use a simple text with emoji
        return Text("💬 " + display_text)
        
    elif hasattr(part, "executable_code") or hasattr(part, "tool_code"):
        # Get the code content from the appropriate attribute
        tool_code_attr = getattr(part, "tool_code", getattr(part, "executable_code", None))
        if tool_code_attr:
            return Text("🛠️ ") + Syntax(tool_code_attr, "python", theme="monokai", line_numbers=True)
            
    elif hasattr(part, "code_execution_result") or hasattr(part, "tool_response"):
        # Get the response content from the appropriate attribute
        tool_response_attr = getattr(part, "tool_response", getattr(part, "code_execution_result", None))
        if tool_response_attr:
            return Text("📋 ") + Text(str(tool_response_attr))
            
    elif hasattr(part, "function_response") and part.function_response is not None:
        return Text("⚙️ ") + Text(str(part.function_response))
        
    elif hasattr(part, "function_call") and part.function_call is not None:
        # Handle function_call parts with lightning emoji and "Tool call"
        function_call_str = f"Tool call: {part.function_call.name}"
        if hasattr(part.function_call, 'args'):
            function_call_str += f"\n{part.function_call.args}"
        return Text("⚡ ") + Text(function_call_str)
        
    # Default case if no specific content type is identified
    # Return None to indicate this part should be skipped
    return None

def create_metadata_table(event):
    """
    Create a table with event metadata including ID, author, status and timestamp
    
    Args:
        event: The event object
        
    Returns:
        Rich table with event metadata
    """
    table = Table(box=box.SIMPLE, show_header=True, header_style="bold")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="white")
    
    table.add_row("Event ID", str(event.id)[:8] + "...")
    table.add_row("Author", str(event.author))
    table.add_row("Final", str(event.is_final_response()))
    table.add_row("Timestamp", time.strftime("%H:%M:%S"))
    
    return table

async def process_agent_response(event):
    """
    Process agent response events and display them using Rich components.
    Returns extracted text if the event is final.
    
    Args:
        event: The agent response event
        
    Returns:
        Extracted text if the event is final, otherwise None
    """
    # Create a unique ID for this event processing
    event_id = str(uuid.uuid4())[:8]
    
    # Create layout for this event
    layout = create_event_layout()
    
    # Set header
    layout["header"].update(
        Text(f"🔹 Agent Response (Event {event_id})", style="bold cyan")
    )
    
    # Process content parts
    content_renderables = []
    extracted_text_parts = []
    
    if event.content and event.content.parts:
        for part in event.content.parts:
            # Check if this is the final response to apply special formatting
            is_final = event.is_final_response()
            
            # Process this content part
            renderable = await process_event_content(event, part, is_final)
            
            # Only add renderable if it's not None (skip unknown content types)
            if renderable is not None:
                content_renderables.append(renderable)
            
            # If this is the final response and has text, extract it
            if is_final and hasattr(part, "text") and part.text:
                extracted_text_parts.append(part.text.strip())
    
    # Combine all extracted text parts
    extracted_text = "\n".join(extracted_text_parts) if extracted_text_parts else None
    
    # If no valid content parts, return early without displaying anything
    if not content_renderables:
        return None
    
    # Update the layout with content and metadata
    # Combine all renderables into a single display
    if len(content_renderables) == 1:
        content = content_renderables[0]
    elif len(content_renderables) > 1:
        # Create a combined display with all content parts
        from rich.columns import Columns
        content = Columns(content_renderables)
    else:
        # This shouldn't happen due to the early return above, but just in case
        return None
    
    # Display the response directly without using layout to prevent cutting off
    # Debug log to see event structure
    print("Event debug info:")
    print("Author:", event.author)
    
    
    # Get agent name - try different attributes that might contain it
    agent_name = (
        getattr(event.author, 'name', None) or  # try author.name
        getattr(event, 'agent_name', None) or    # try event.agent_name
        str(event.author) if event.author else   # try string representation of author
        'Agent'                                  # fallback
    )
    
    # Add (Final) tag if this is a final response
    response_label = f"{agent_name} Response"
    if event.is_final_response():
        response_label += " (Final)"
    
    console.print(Text(f"\n📋 {response_label}"), new_line_start=True)
    console.print(content, overflow="fold", no_wrap=False, crop=False)
    
    # Return extracted text if this was the final response
    return extracted_text

# Global variable to track active live display
_active_live_display = None

def stop_active_live_display():
    """Safely stop any active live display"""
    global _active_live_display
    if _active_live_display is not None:
        try:
            _active_live_display.stop()
        except Exception:
            pass
        _active_live_display = None

async def display_thinking_indicator():
    """
    Display a thinking indicator with brain emoji while the agent is thinking
    """
    global _active_live_display
    
    # If there's already an active live display, don't create a new one
    if _active_live_display is not None:
        return
        
    # Default to generic "Agent" text for thinking indicator
    spinner = Spinner("dots", "🧠 Agent thinking")
    try:
        # Ensure any existing display is stopped
        stop_active_live_display()
        
        # Create and start new display
        _active_live_display = Live(
            spinner, 
            refresh_per_second=10, 
            console=console, 
            transient=True,
            auto_refresh=True
        )
        _active_live_display.start()
        
        while True:
            spinner.update()
            await asyncio.sleep(0.1)
            
    except asyncio.CancelledError:
        # Clean up when cancelled
        stop_active_live_display()
        console.print("\r", end="", flush=True)
        raise
    except Exception:
        stop_active_live_display()
        raise
    finally:
        # Extra safety to ensure cleanup
        if _active_live_display is not None:
            stop_active_live_display()

def display_agent_call_started(user_id, session_id, message):
    """
    Display the initial agent call information
    
    Args:
        user_id: The user ID
        session_id: The session ID
        message: The user message
    """
    console.print(Text(f"🔹 Calling agent for User: {user_id}, Session: {session_id}"))
    console.print(Text(f"💬 {message}"), new_line_start=False)

def display_completion_message(success=True):
    """
    Display agent execution completion message
    
    Args:
        success: Whether the execution was successful
    """
    if success:
        console.print(Text("✅ Done", style="green"), new_line_start=True)
    else:
        console.print(Text("❌ No response generated", style="red"), new_line_start=True)

def display_fallback_response(text):
    """
    Display the fallback final response when process_agent_response didn't pick it up
    
    Args:
        text: The response text
    """
    console.print(Text("📝 ") + Markdown(text))

def display_missing_response():
    """
    Display a message when no clear text was found in the final event
    """
    console.print(Text(
        "⚠️  Final event received, but no straightforward text found in its parts.\n"
        "The actual final data might have been in an earlier event.",
        style="yellow"
    ))

def display_error_message(message):
    """
    Display an error message with distinctive styling
    
    Args:
        message: The error message to display
    """
    console.print(Text(f"❌ Error: {message}", style="red"))
