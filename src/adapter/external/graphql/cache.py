# import asyncio
# from typing import TypeVar

# from pydantic import BaseModel
# from strawberry.dataloader import AbstractCache
# from typing_extensions import deprecated

# import src.domain.model as domain
# from src.protocol.internal.cache.generic import CacheProtocol

# T = TypeVar("T", bound=BaseModel)

# NOTE: Strawberry current Dataloader implementation does not support async cache resolution
# traking issue: https://github.com/strawberry-graphql/strawberry/issues/3290


# class CacheMap[T](AbstractCache[domain.ObjectID, T]):

#     def __init__(self, cache_service: CacheProtocol[T]):
#         self._cache_service = cache_service

#     def get(self, key: domain.ObjectID) -> asyncio.Future[T] | None:
#         future = asyncio.get_event_loop().create_future()
#         data = self._cache_service.get(key)
#         if data is None:
#             return data

#         async def promise():
#             return data

#         return asyncio.ensure_future(promise())

#     def set(self, key: domain.ObjectID, future_value: asyncio.Future[T]) -> None:
#         async def put_to_cache(value: T):
#             await self._cache_service.put(key, value)

#         future_value.add_done_callback(put_to_cache)

#     def delete(self, key: domain.ObjectID) -> None:
#         return self._cache_service.delete(key)

#     def clear(self) -> None:
#         return self._cache_service.flush()
