from pydantic import BaseModel, Field


class ImageSize(BaseModel):
    w: int = Field(gt=0)
    url: str


class ImageMedia(BaseModel):
    url: str
    width: int = Field(gt=0)
    height: int = Field(gt=0)
    dominantColor: str = Field(pattern=r"^#[0-9a-fA-F]{6}$")
    sizes: list[ImageSize] = Field(default_factory=list)
