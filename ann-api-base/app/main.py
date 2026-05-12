from __future__ import annotations

import traceback

import numpy as np
from fastapi import Depends, FastAPI, Header, HTTPException, status

from .config import settings
from .model_runtime import runtime
from .optimization_runtime import optimize, rerank
from .schemas import (
    HealthResponse,
    OptimizeRequest,
    OptimizeResponse,
    PredictRequest,
    PredictResponse,
    RerankRequest,
    RerankResponse,
)

app = FastAPI(title='Flux Mind ANN API', version='0.2.0')


def require_api_key(x_api_key: str = Header(default='')) -> None:
    if not settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='ANN_API_KEY is not configured on the server',
        )
    if x_api_key != settings.api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid API key')


@app.get('/health', response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status='ok',
        runtime_mode=settings.runtime_mode,
        model_loaded=runtime.is_loaded,
    )


@app.post('/predict', response_model=PredictResponse, dependencies=[Depends(require_api_key)])
def predict(payload: PredictRequest) -> PredictResponse:
    print(
        f"[ANN API] Received /predict request with {len(payload.inputs)} rows "
        f"(request_id={payload.request_id})",
        flush=True,
    )
    if len(payload.inputs) > settings.max_points:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f'Too many input points. Limit is {settings.max_points}.',
        )

    x_values = np.asarray(payload.inputs, dtype=np.float32)
    try:
        y_values = runtime.predict(x_values, batch_size=payload.batch_size)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    except Exception as exc:
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'Prediction failed: {exc}') from exc

    print(
        f"[ANN API] Finished /predict request with {len(payload.inputs)} rows "
        f"(request_id={payload.request_id})",
        flush=True,
    )
    return PredictResponse(
        predictions=np.round(y_values, 6).tolist(),
        count=len(payload.inputs),
        request_id=payload.request_id,
    )


@app.post('/optimize', response_model=OptimizeResponse, dependencies=[Depends(require_api_key)])
def optimize_endpoint(payload: OptimizeRequest) -> OptimizeResponse:
    print('[ANN API] Received /optimize request', flush=True)
    try:
        result = optimize(payload.user_params, batch_size=payload.batch_size)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    except Exception as exc:
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'Optimization failed: {exc}') from exc
    return OptimizeResponse(**result)


@app.post('/rerank', response_model=RerankResponse, dependencies=[Depends(require_api_key)])
def rerank_endpoint(payload: RerankRequest) -> RerankResponse:
    print(f'[ANN API] Received /rerank request for result_id={payload.result_id}', flush=True)
    try:
        result = rerank(
            result_id=payload.result_id,
            preference=payload.preference,
            strength=payload.strength,
            top_n=payload.top_n,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    except Exception as exc:
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'Rerank failed: {exc}') from exc
    return RerankResponse(**result)
