from typing import Literal
from pydantic import BaseModel

class Probe(BaseModel):
    probeId: str
    strategy: str
    prompt: str
    attackHypothesis: str
    expectedOutcome: Literal["BLOCKED", "BYPASSED", "REFUSE_OR_SAFE_REDIRECT"]