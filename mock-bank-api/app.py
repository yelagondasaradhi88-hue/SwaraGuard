import asyncio
import time
from typing import Optional
from fastapi import FastAPI, Header, HTTPException, Query, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from database import BankDatabase, BankException
from models import (
    AccountResponse,
    AccountStatus,
    ApiErrorDetail,
    ApiErrorResponse,
    CreateAccountRequest,
    FreezeAccountRequest,
    StatementResponse,
    TransactionResponse,
    TransferRequest,
)

# Initialize FastAPI App
app = FastAPI(
    title="SwaraGuard Mock Retail Bank API (INR)",
    description=(
        "Simulates realistic retail banking flows in Indian Rupees (₹) with integer paise precision, "
        "atomic balance updates, idempotency support, and resilience testing flags."
    ),
    version="1.0.0",
)

# Enable CORS for local testing, frontend integration, and Netlify dashboards
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Idempotency-Key", "X-Cache-Lookup", "X-Simulation-Status"],
)

# Database instance
db = BankDatabase()


# --- Exception Handlers for Clean JSON Responses ---

@app.exception_handler(BankException)
async def bank_exception_handler(request: Request, exc: BankException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            }
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        field = ".".join(str(loc) for loc in err.get("loc", []))
        errors.append({"field": field, "issue": err.get("msg")})

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request payload validation failed.",
                "details": {"validationErrors": errors},
            }
        },
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": str(exc),
                "details": {},
            }
        },
    )


# --- Root & Health Endpoints ---

@app.get("/", tags=["Health"])
def root():
    return {
        "service": "SwaraGuard Mock Retail Bank API",
        "currency": "INR (₹)",
        "precision": "Paise integer math (0 floating drift)",
        "status": "ONLINE",
        "docsUrl": "/docs",
        "sampleAccounts": [
            "ACC-IND-1001 (Saradhi Yelagonda - Savings ₹75,000.00)",
            "ACC-IND-1002 (Acme Retail Tech - Current ₹2,50,000.00)",
            "ACC-IND-1003 (Cyber Safe Emergency Reserve - Savings ₹1,00,000.00)",
        ],
    }


@app.get("/health", tags=["Health"])
def health():
    return {"status": "HEALTHY", "timestamp": time.time()}


# --- Account Endpoints ---

@app.post(
    "/api/accounts",
    response_model=AccountResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Accounts"],
    summary="Create a new bank account with optional initial deposit",
)
def create_account(req: CreateAccountRequest):
    return db.create_account(
        holder_name=req.holderName,
        account_type=req.accountType,
        ifsc=req.ifsc or "MOCK0001234",
        initial_deposit_inr=req.initialDeposit,
    )


@app.get(
    "/api/accounts/{account_id}",
    response_model=AccountResponse,
    tags=["Accounts"],
    summary="Fetch account details and current balance",
)
def get_account(account_id: str):
    return db.get_account(account_id)


@app.get(
    "/api/accounts/{account_id}/statement",
    response_model=StatementResponse,
    tags=["Accounts"],
    summary="Get paginated transaction history and account statement",
)
def get_statement(
    account_id: str,
    mode: Optional[str] = Query(None, description="Filter by mode: UPI, IMPS, NEFT, INTERNAL"),
    from_date: Optional[str] = Query(None, alias="from", description="ISO start date timestamp"),
    to_date: Optional[str] = Query(None, alias="to", description="ISO end date timestamp"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    offset: int = Query(0, ge=0, description="Page offset"),
):
    return db.get_statement(
        account_id=account_id,
        mode=mode,
        from_date=from_date,
        to_date=to_date,
        limit=limit,
        offset=offset,
    )


@app.post(
    "/api/accounts/{account_id}/freeze",
    response_model=AccountResponse,
    tags=["Account Security"],
    summary="Emergency Freeze account (halts all outgoing & incoming transfers)",
)
def freeze_account(account_id: str, req: Optional[FreezeAccountRequest] = None):
    return db.set_account_status(account_id, AccountStatus.FROZEN)


@app.post(
    "/api/accounts/{account_id}/unfreeze",
    response_model=AccountResponse,
    tags=["Account Security"],
    summary="Unfreeze account back to ACTIVE state",
)
def unfreeze_account(account_id: str):
    return db.set_account_status(account_id, AccountStatus.ACTIVE)


# --- Transfer Endpoints ---

@app.post(
    "/api/transfers",
    response_model=TransactionResponse,
    status_code=status.HTTP_200_OK,
    tags=["Transfers"],
    summary="Atomically transfer funds between accounts",
    responses={
        400: {"model": ApiErrorResponse, "description": "Invalid parameters or self-transfer"},
        403: {"model": ApiErrorResponse, "description": "Account is FROZEN"},
        404: {"model": ApiErrorResponse, "description": "Account not found"},
        422: {"model": ApiErrorResponse, "description": "Insufficient funds or validation failure"},
        503: {"model": ApiErrorResponse, "description": "Simulated transient failure"},
    },
)
async def transfer_funds(
    req: TransferRequest,
    response: Response,
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    x_simulate_failure: Optional[str] = Header(None, alias="X-Simulate-Failure"),
    x_simulate_delay_ms: Optional[int] = Header(None, alias="X-Simulate-Delay"),
    simulate_failure: Optional[bool] = Query(False, description="Query flag for simulated failure"),
):
    # 1. Simulate Artificial Latency / Delay if requested
    if x_simulate_delay_ms and x_simulate_delay_ms > 0:
        delay_sec = min(x_simulate_delay_ms / 1000.0, 5.0)  # cap at 5s
        await asyncio.sleep(delay_sec)

    # 2. Simulate Transient Gateway Failure if requested
    should_fail = simulate_failure or (x_simulate_failure and x_simulate_failure.lower() in ("true", "1", "yes"))
    if should_fail:
        raise BankException(
            code="SIMULATED_TRANSIENT_FAILURE",
            message="Simulated bank switch gateway timeout. Please retry with Idempotency-Key.",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details={"simulated": True, "network": req.mode.value},
        )

    # 3. Check Idempotency Key
    if idempotency_key:
        cached = db.get_idempotency_record(idempotency_key)
        if cached:
            cached_status, cached_json = cached
            response.headers["X-Cache-Lookup"] = "HIT"
            response.status_code = cached_status
            return cached_json

    # 4. Execute Atomic Transfer
    txn = db.execute_transfer(
        from_account_id=req.fromAccountId,
        to_account_id=req.toAccountId,
        amount_inr=req.amount,
        mode=req.mode,
        reference_note=req.referenceNote,
    )

    # 5. Store Idempotency Record if key provided
    if idempotency_key:
        db.save_idempotency_record(
            key=idempotency_key,
            status_code=200,
            response_data=txn.model_dump(),
        )
        response.headers["X-Cache-Lookup"] = "MISS"

    return txn


if __name__ == "__main__":
    import uvicorn
    print("🏦 Starting SwaraGuard Mock Bank API on http://127.0.0.1:8001")
    uvicorn.run("app:app", host="127.0.0.1", port=8001, reload=True)

