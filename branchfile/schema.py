from typing import List, Dict, Union, Literal, Any, Optional
import pydantic

class BfListItem(pydantic.BaseModel):
    slot: int
    tag: str
    val: Any

class BfList(pydantic.BaseModel):
    type: Literal['list']
    key: str
    fields: List[BfListItem]

BfValue = Union[str, BfList, List[Any]]

class BfDocBranch(pydantic.BaseModel):
    key: str
    tag: str
    weight: Optional[float]
    doc: Dict[str, BfValue]

class BfAddressBranch(pydantic.BaseModel):
    key: str
    tag: str
    weight: Optional[float]
    address: List[Union[str, int]]
    value: Any

class BfBoolBranch(pydantic.BaseModel):
    key: str
    weight: Optional[float] # weight of true
    address: List[Union[str, int]]

BfBranch = Union[BfDocBranch, BfAddressBranch, BfBoolBranch]

class Root(pydantic.BaseModel):
    base: Dict[str, BfValue]
    branches: List[BfBranch]
