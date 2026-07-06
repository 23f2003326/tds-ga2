import time
import uuid
from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware

EMAIL =  "23f2003326@ds.study.iitm.ac.in"

ALLOWED_ORIGIN = "https://dash-prhf07.example.com"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGIN],
    allow_credentials=False,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)

@app.middleware("http")
async def process_time(request: Request, call_next):
    start = time.perf_counter()

    response = await call_next(request)

    response.headers["X-Request-ID"] = str(uuid.uuid4())
    response.headers["X-Process-Time"] = str(time.perf_counter() - start)

    return response


@app.get("/stats")
def stats(values: str = Query(...)):

    numbers = [int(i) for i in values.split(",")]

    return {
        "email": EMAIL,
        "count": len(numbers),
        "sum": sum(numbers),
        "min": min(numbers),
        "max": max(numbers),
        "mean": sum(numbers)/len(numbers)
    }