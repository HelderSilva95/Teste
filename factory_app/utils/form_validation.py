"""
Helper para validação de Forms com Pydantic
"""
from typing import Type, TypeVar
from pydantic import BaseModel, ValidationError
from fastapi import Form, HTTPException
from inspect import signature

T = TypeVar('T', bound=BaseModel)


def as_form(cls: Type[T]):
    """
    Decorator para permitir Pydantic models em Form data

    Usage:
        @as_form
        class MySchema(BaseModel):
            field1: str
            field2: int

    Then in route:
        async def route(data: MySchema = Depends()):
            ...
    """
    new_params = []

    for field_name, field_info in cls.model_fields.items():
        default = field_info.default if field_info.default is not None else ...
        annotation = field_info.annotation

        new_params.append(
            signature(lambda x=Form(default): x).parameters['x'].replace(
                annotation=annotation,
                name=field_name
            )
        )

    async def _as_form(**data):
        try:
            return cls(**data)
        except ValidationError as e:
            errors = []
            for error in e.errors():
                field = error['loc'][0] if error['loc'] else 'unknown'
                msg = error['msg']
                errors.append(f"{field}: {msg}")
            raise HTTPException(status_code=422, detail="; ".join(errors))

    sig = signature(_as_form)
    sig = sig.replace(parameters=new_params)
    _as_form.__signature__ = sig

    return _as_form
