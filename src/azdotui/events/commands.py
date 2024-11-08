# events/commands.py

import curses

COMMANDS = {
    9: "switch_pane",                    # Tab key
    ord('q'): "exit",                    # Quit application
    curses.KEY_UP: ("navigate", 'UP'),   # Up arrow
    curses.KEY_DOWN: ("navigate", 'DOWN'),# Down arrow
    curses.KEY_LEFT: "handle_input",     # Left arrow
    curses.KEY_RIGHT: "handle_input",    # Right arrow
    curses.KEY_ENTER: "handle_selection",
    10: "handle_selection",              # Enter key
    13: "handle_selection",
    ord(' '): "handle_input",            # Spacebar
    ord('t'): "trigger_pipelines",       # Trigger pipelines
    ord('c'): "cancel_builds",           # Cancel builds
    # Add more keybindings as needed
}

