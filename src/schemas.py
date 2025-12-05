from pydantic import BaseModel


class Monitor(BaseModel):
    id: int
    width: int
    height: int


class MonitorsOut(BaseModel):
    count: int
    monitors: list[Monitor]
