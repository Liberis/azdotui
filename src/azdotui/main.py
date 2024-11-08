# main.py

import asyncio
import curses

from azdotui.api.azdo import AzureDevOpsClient
from azdotui.config.logger import logger
from azdotui.events.keybindings import handle_key
from azdotui.ui.layout import Layout
from azdotui.utils.cursed import init_colors


async def main(screen):
    init_colors()
    curses.curs_set(0)  # Hide the cursor
    azdo_client = AzureDevOpsClient()
    layout = Layout(screen, azdo_client)

    try:
        # Initial data load
        await layout.panes['projects'].refresh_data()  # Updated line
        if layout.panes['projects'].items:             # Updated line
            await layout.panes['projects'].handle_selection()  # Updated line

        while layout.running:
            layout.render()
            key = screen.getch()
            await handle_key(layout, key)  # Await the async handle_key function
            await asyncio.sleep(0)  # Yield control to the event loop
    except Exception:
        logger.error("An unexpected error occurred during program execution.", exc_info=True)
        layout.running = False  # Ensure the loop exits
    finally:
        # Cancel auto-refresh tasks
        for task in layout.auto_refresh_tasks:
            task.cancel()
        # Wait for tasks to be cancelled
        await asyncio.gather(*layout.auto_refresh_tasks, return_exceptions=True)
        await azdo_client.close()  # Ensure the client session is closed

def main_entry():
    curses.wrapper(lambda scr: asyncio.run(main(scr)))

if __name__ == '__main__':
    main_entry()

