from pydantic import BaseModel

class Song(BaseModel):
    title: str
    path: str
