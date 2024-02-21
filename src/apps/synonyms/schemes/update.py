from typing import Optional, List

from pydantic import BaseModel, conlist, constr


class SynonymUpdate(BaseModel):
    name: Optional[constr(min_length=1)]
    input: Optional[List[str]]
    synonyms: Optional[conlist(str, min_items=1)]
