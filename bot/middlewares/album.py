import asyncio
from typing import List, Union

from aiogram import Bot, Dispatcher, types
from aiogram import BaseMiddleware
from aiogram.dispatcher.event.bases import CancelHandler
from loguru import logger


class AlbumMiddleware(BaseMiddleware):
    def __init__(self, latency: Union[int, float] = 0.01):
        # Initialize latency and album_data dictionary
        self.latency = latency
        self.album_data = {}
        super().__init__()

    def collect_album_messages(self, event: types.Message):
        """
        Collect messages of the same media group.
        """
        # Check if media_group_id exists in album_data
        if event.media_group_id not in self.album_data:
            # Create a new entry for the media group
            self.album_data[event.media_group_id] = {"messages": []}
        # Append the new message to the media group
        self.album_data[event.media_group_id]["messages"].append(event)
        # Return the total number of messages in the current media group
        return len(self.album_data[event.media_group_id]["messages"])

    async def __call__(self, handler, event: types.Message, data: dict[str, any]) -> any:
        """
        Main middleware logic.
        """
        # If the event has no media_group_id, pass it to the handler immediately
        if not event.media_group_id:
            return await handler(event, data)

        # Collect messages of the same media group
        total_before = self.collect_album_messages(event)

        # Wait for a specified latency period
        await asyncio.sleep(self.latency)

        # Check the total number of messages after the latency
        total_after = self.collect_album_messages(event)

        # If new messages were added during the latency, exit
        if total_before != total_after:
            return

        # Sort the album messages by message_id and add to data
        album_messages = self.album_data[event.media_group_id]["messages"]
        album_messages.sort(key=lambda x: x.message_id)
        data["album"] = list(album_messages)

        logger.debug(data["album"])

        # Remove the media group from tracking to free up memory
        del self.album_data[event.media_group_id]
        # Call the original event handler
        return await handler(event, data)


