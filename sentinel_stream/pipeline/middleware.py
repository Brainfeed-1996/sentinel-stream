from __future__ import annotations
import asyncio
from typing import Protocol, List
from ..model import Event

class PipelineMiddleware(Protocol):
    async def process(self, event: Event, next_call):
        ...

class LoggingMiddleware:
    async def process(self, event: Event, next_call):
        # Pre-processing
        result = await next_call(event)
        # Post-processing
        return result

class EnrichmentMiddleware:
    async def process(self, event: Event, next_call):
        # Enrich event data here
        return await next_call(event)

class AsyncPipeline:
    def __init__(self, handlers: List[PipelineMiddleware]):
        self.handlers = handlers

    async def execute(self, event: Event, final_handler):
        async def dispatch(index, current_event):
            if index < len(self.handlers):
                handler = self.handlers[index]
                return await handler.process(current_event, lambda e: dispatch(index + 1, e))
            else:
                return await final_handler(current_event)
        
        return await dispatch(0, event)
