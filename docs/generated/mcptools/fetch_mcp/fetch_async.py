from typing import Optional

from pydantic import AnyUrl, BaseModel, ConfigDict, Field, conint

from . import CLIENT


class Params(BaseModel):
    model_config = ConfigDict(
        use_enum_values=True,
    )
    url: AnyUrl = Field(..., title="Url")
    """
    URL to fetch
    """
    max_length: Optional[conint(lt=1000000, gt=0)] = Field(5000, title="Max Length")
    """
    Maximum number of characters to return.
    """
    start_index: Optional[conint(ge=0)] = Field(0, title="Start Index")
    """
    On return output starting at this character index.
    """
    raw: Optional[bool] = Field(False, title="Raw")
    """
    Get the actual HTML content of the requested page, without simplification.
    """


# --8<-- [start:run]
async def run(params: Params) -> str:
    """Fetches a URL from the internet and extracts its contents as markdown."""
    return await CLIENT.run(tool_name="fetch", tool_args=params.model_dump(exclude_none=True))
# --8<-- [end:run]
