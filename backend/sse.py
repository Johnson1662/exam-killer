"""SSE event manager — per-course asyncio.Queue for progress events."""

import asyncio
from collections import defaultdict

_queues: dict[int, asyncio.Queue] = defaultdict(asyncio.Queue)


def get_queue(course_id: int) -> asyncio.Queue:
    """Return (or create) the SSE queue for *course_id*."""
    return _queues[course_id]


async def push_event(course_id: int, event: str, data: str):
    """Push an SSE event to the course's queue."""
    q = get_queue(course_id)
    await q.put((event, data))


async def push_message(course_id: int, data: str):
    """Push a default 'message' event."""
    await push_event(course_id, "message", data)


async def event_stream(course_id: int):
    """Async generator yielding SSE-format lines.

    Yields ``event: X\ndata: Y\n\n`` strings.
    """
    q = get_queue(course_id)
    while True:
        event, data = await q.get()
        yield f"event: {event}\ndata: {data}\n\n"
        if data == "done":
            break
    # Clean up queue so it doesn't accumulate
    _queues.pop(course_id, None)
