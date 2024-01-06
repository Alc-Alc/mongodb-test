from collections.abc import AsyncIterator
from contextlib import asynccontextmanager, closing
from typing import Annotated

from bson import ObjectId
from litestar import Litestar, get, post
from litestar.contrib.pydantic import PydanticDTO
from litestar.datastructures import State
from litestar.dto import DTOData
from litestar.exceptions import NotFoundException
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, ConfigDict, Field
from pydantic.functional_validators import BeforeValidator

PyObjectId = Annotated[str, BeforeValidator(str)]


class ItemModel(BaseModel):
    id: PyObjectId | None = Field(alias="_id", default=None)
    name: str = Field(...)
    email: str = Field(...)
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {"name": "Jane Doe", "email": "jdoe@example.com"}
        },
    )


@post(dto=PydanticDTO[ItemModel])
async def create_item(data: DTOData[ItemModel], state: State) -> ItemModel:
    new_bar = await state.db_collection.insert_one(data.as_builtins())
    created_bar = await state.db_collection.find_one({"_id": new_bar.inserted_id})
    return ItemModel.model_validate(created_bar)


@get("{id: str}", return_dto=PydanticDTO[ItemModel])
async def show_item(id: str, state: State) -> ItemModel:
    if (item := await state.db_collection.find_one({"_id": ObjectId(id)})) is not None:
        return item

    raise NotFoundException(f"item {id} not found")


@asynccontextmanager
async def db_connection(app: Litestar) -> AsyncIterator[None]:
    conn_string = "mongodb://root:password@localhost:27017/?readPreference=primary&appname=MongoDB%20Compass&ssl=false"
    with closing(AsyncIOMotorClient(conn_string)) as db_client:
        app.state.db_collection = db_client.mcve_db.get_collection("bars")
        yield


app = Litestar([create_item, show_item], lifespan=[db_connection])
