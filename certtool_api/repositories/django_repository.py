from typing import Generic, Protocol, TypeVar

from django.db import models  # noqa: F401

EntityType = TypeVar("EntityType")


class DomainModeler(Protocol):
    def to_entity(self) -> EntityType:
        ...

    def save_from_entity(self, entity: EntityType):
        ...


ModelType = TypeVar("ModelType", bound=DomainModeler)


class DjangoRepository(Generic[EntityType, ModelType]):
    """
    A DjangoRepository that uses a Django Model to store and retrieve an Entity.
    """

    def __init__(self, data_model: ModelType):
        self._data_model: ModelType = data_model

    def save(self, entity: EntityType):
        self._data_model.save_from_entity(entity)

    def get(self, id: int) -> EntityType:
        return self._data_model.objects.get(id=id).to_entity()  # type: ignore

    def all(self) -> list[EntityType]:
        return [e.to_entity() for e in self._data_model.objects.all()]  # type: ignore
