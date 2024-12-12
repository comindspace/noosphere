from pydantic import BaseModel, Field, NonNegativeInt

class StatisticsRecord(BaseModel):
    id: NonNegativeInt = Field(alias="")
    question: str
    naive: bool
    local: bool
    global_: bool = Field(alias="global")
    hybrid: bool
    
    def in_total(self):
        return (self.naive
                or self.local
                or self.global_
                or self.hybrid)
