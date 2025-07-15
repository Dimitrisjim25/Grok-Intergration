from typing import TypedDict

class Config(TypedDict):
    api_url: str
    timeout: int

class GrokResponse(TypedDict):
    response: str
