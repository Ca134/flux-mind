from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class _BaseSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=())


class PredictRequest(_BaseSchema):
    inputs: list[list[float]] = Field(..., description='Batch input rows with shape (N, 9)')
    batch_size: int | None = Field(default=None, ge=1, le=50000)
    request_id: str | None = Field(default=None, max_length=200)

    @field_validator('inputs')
    @classmethod
    def validate_inputs(cls, value: list[list[float]]) -> list[list[float]]:
        if not value:
            raise ValueError('inputs must not be empty')
        for row in value:
            if len(row) != 9:
                raise ValueError('each input row must have exactly 9 values')
        return value


class PredictResponse(_BaseSchema):
    predictions: list[list[float]]
    count: int
    request_id: str | None = None


class OptimizeRequest(_BaseSchema):
    user_params: dict[str, Any] = Field(default_factory=dict)
    batch_size: int | None = Field(default=None, ge=1, le=50000)


class DesignRecord(_BaseSchema):
    rank: int
    type: str | None = None
    params: dict[str, Any]
    performance: dict[str, Any]


class OptimizeResponse(_BaseSchema):
    status: str
    result_id: str | None = None
    total_candidates: int | None = None
    pareto_count: int | None = None
    top_designs: list[DesignRecord] = Field(default_factory=list)
    message: str | None = None


class RerankRequest(_BaseSchema):
    result_id: str = Field(..., min_length=1)
    preference: str = Field(default='default')
    strength: str = Field(default='medium')
    top_n: int = Field(default=10, ge=1, le=50)


class RerankResponse(_BaseSchema):
    status: str
    result_id: str | None = None
    designs: list[DesignRecord] = Field(default_factory=list)
    message: str | None = None


class HealthResponse(_BaseSchema):
    status: str
    runtime_mode: str
    model_loaded: bool
