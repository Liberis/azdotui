# events/keybindings.py

import curses

from azdotui.events.commands import COMMANDS
from azdotui.utils.enums import InputAction
from azdotui.utils.helpers import call_async_if_coroutine


async def handle_key(layout, key):
    if layout.input_mode:
        await handle_input_mode(layout, key)
    else:
        command = COMMANDS.get(key)
        if command:
            if command == "switch_pane":
                layout.switch_pane()
            elif command == "exit":
                layout.running = False
            elif command == "handle_input":
                await call_async_if_coroutine(layout.active_pane, 'handle_input', key)
            elif command == "handle_selection":
                await call_async_if_coroutine(layout.active_pane, 'handle_selection')
            elif isinstance(command, tuple) and command[0] == "navigate":
                direction = command[1]
                layout.active_pane.navigate(direction)
            elif command == "trigger_pipelines":
                layout.set_input_mode(prompt="Enter branch/tag: ", action=InputAction.TRIGGER_PIPELINES)
            elif command == "cancel_builds":
                layout.set_input_mode(prompt="Confirm cancelling all running and queued builds? (y/n): ", action=InputAction.CANCEL_BUILDS)
            else:
                pass  # Handle other commands
        else:
            pass  # Key not mapped to any command

async def handle_input_mode(layout, key):
    if layout.confirmation_mode:
        if key in [ord('y'), ord('Y')]:
            # User confirmed action
            if layout.input_action == InputAction.TRIGGER_PIPELINES:
                await layout.trigger_selected_pipelines()
                layout.status_bar.set_message("Triggering pipelines...")
            elif layout.input_action == InputAction.CANCEL_BUILDS:
                await layout.cancel_running_and_queued_builds()
                layout.status_bar.set_message("Cancelling builds...")
            # Reset input mode
            layout.input_mode = False
            layout.confirmation_mode = False
        elif key in [ord('n'), ord('N')]:
            layout.status_bar.set_message("Cancelled.")
            layout.input_mode = False
            layout.confirmation_mode = False
        else:
            pass  # Ignore other keys
    elif key in [10, 13]:  # Enter key
        # User finished typing input
        if layout.input_buffer or layout.input_action == InputAction.CANCEL_BUILDS:
            layout.confirmation_mode = True
            if layout.input_action == InputAction.TRIGGER_PIPELINES:
                layout.status_bar.set_message(f"Confirm triggering on '{layout.input_buffer}'? (y/n)")
            elif layout.input_action == InputAction.CANCEL_BUILDS:
                layout.status_bar.set_message("Confirm cancelling all running and queued builds? (y/n)")
        else:
            layout.status_bar.set_message("Input cannot be empty. Try again.")
            layout.input_buffer = ''
    elif key in [27]:  # Escape key
        # User cancelled input
        layout.status_bar.set_message("Cancelled.")
        layout.input_mode = False
    elif key in [curses.KEY_BACKSPACE, 127]:
        # Handle backspace
        layout.input_buffer = layout.input_buffer[:-1]
        layout.status_bar.set_message(layout.input_prompt + layout.input_buffer)
    elif 32 <= key <= 126:
        # Acceptable character input
        layout.input_buffer += chr(key)
        layout.status_bar.set_message(layout.input_prompt + layout.input_buffer)
    else:
        pass  # Ignore other keys

