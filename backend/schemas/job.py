from pydantic import BaseModel

class JobBase(BaseModel):
    title: str
    description: str

class JobCreate(JobBase):
    pass

class JobResponse(JobBase):
    id: int
    owner_id: int
    class Config:
        orm_mode = True
