import time
import uuid
import os
import yaml
import jwt

from typing import List
from dotenv import load_dotenv
from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

EMAIL = "23f2003326@ds.study.iitm.ac.in"

ALLOWED_ORIGIN = "https://dash-prhf07.example.com"

ISSUER = "https://idp.exam.local"
AUDIENCE = "tds-wiqto7r3.apps.exam.local"

PUBLIC_KEY = """
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA2okOHspNjgA+2rTLbeuY
cxiP/hG8C6Sb9iwg3yiLAA4HCnpITcbWCSelbvbYGuc3EbNy4xFyf5Cbj5DHJMID
EkryOgyd2giIIIBOUBj8S63uGcnRpOBh9NFatfNwheKuzsPuVNldu6A9cNteNpXc
WyJjG2axVfmq7i6SuKr1JoWYG7xTTAvKPujSl4OtsQfO3h5NepzdfXpr28oNnzfW
ed+zclR6BcmNNo/WVfJ4xyCLSf0BCOgdTgW6PdaChd1l9VDetJZVEgC5tkyvXsfI
SI6iyrYbKR0NEBSqq4XkadEjsCs4F1RncsS4LlgniT7GlkL9Mce3b0wGLs9/7ZIX
dQIDAQAB
-----END PUBLIC KEY-----
"""

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://dash-prhf07.example.com",
        "https://exam.sanand.workers.dev",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def process_time(request: Request, call_next):
    start = time.perf_counter()

    response = await call_next(request)

    response.headers["X-Request-ID"] = str(uuid.uuid4())
    response.headers["X-Process-Time"] = f"{time.perf_counter() - start:.6f}"

    return response


# ---------------- Question 1 ---------------- #

@app.get("/stats")
def stats(values: str = Query(...)):
    numbers = [int(x.strip()) for x in values.split(",")]

    return {
        "email": EMAIL,
        "count": len(numbers),
        "sum": sum(numbers),
        "min": min(numbers),
        "max": max(numbers),
        "mean": sum(numbers) / len(numbers)
    }


# ---------------- Question 2 ---------------- #

class TokenRequest(BaseModel):
    token: str


@app.post("/verify")
def verify_token(data: TokenRequest):
    try:
        payload = jwt.decode(
            data.token,
            PUBLIC_KEY,
            algorithms=["RS256"],
            issuer=ISSUER,
            audience=AUDIENCE,
        )

        return {
            "valid": True,
            "email": payload.get("email"),
            "sub": payload.get("sub"),
            "aud": payload.get("aud")
        }

    except Exception:
        return JSONResponse(
            status_code=401,
            content={
                "valid": False
            }
        )


# ---------------- Question 3 ---------------- #

DEFAULTS = {
    "port": 8000,
    "workers": 1,
    "debug": False,
    "log_level": "info",
    "api_key": "default-secret-000",
}


def to_bool(value):
    return str(value).lower() in ["true", "1", "yes", "on"]



@app.get("/effective-config")
def effective_config(set: List[str] = Query(default=[])):

    config = DEFAULTS.copy()

    # YAML
    if os.path.exists("config.development.yaml"):
        with open("config.development.yaml", "r") as f:
            data = yaml.safe_load(f)
            if data:
                config.update(data)

    # .env
    dotenv = {}
    if os.path.exists(".env"):
        with open(".env") as f:
            for line in f:
                line = line.strip()
                if "=" in line:
                    k, v = line.split("=", 1)
                    dotenv[k] = v

    if "APP_PORT" in dotenv:
        config["port"] = int(dotenv["APP_PORT"])

    if "NUM_WORKERS" in dotenv:
        config["workers"] = int(dotenv["NUM_WORKERS"])

    if "APP_API_KEY" in dotenv:
        config["api_key"] = dotenv["APP_API_KEY"]

    # OS Environment
    env_map = {
        "APP_PORT": ("port", int),
        "APP_WORKERS": ("workers", int),
        "APP_LOG_LEVEL": ("log_level", str),
        "APP_API_KEY": ("api_key", str),
    }

    for env_key, (cfg_key, caster) in env_map.items():
        if env_key in os.environ:
            config[cfg_key] = caster(os.environ[env_key])

    # CLI
    for item in set:
        if "=" not in item:
            continue

        key, value = item.split("=", 1)

        if key in ("port", "workers"):
            config[key] = int(value)

        elif key == "debug":
            config["debug"] = value.lower() in ("true", "1", "yes", "on")

        else:
            config[key] = value

    config["api_key"] = "****"

    return config
    config = DEFAULTS.copy()

    # 1. YAML
    if os.path.exists("config.development.yaml"):
        with open("config.development.yaml", "r") as f:
            data = yaml.safe_load(f)
            if data:
                config.update(data)

    # 2. .env values (read directly)
    dotenv = {}
    if os.path.exists(".env"):
        with open(".env") as f:
            for line in f:
                line = line.strip()
                if not line or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                dotenv[k] = v

    if "APP_PORT" in dotenv:
        config["port"] = int(dotenv["APP_PORT"])

    if "NUM_WORKERS" in dotenv:
        config["workers"] = int(dotenv["NUM_WORKERS"])

    if "APP_API_KEY" in dotenv:
        config["api_key"] = dotenv["APP_API_KEY"]

    # 3. OS Environment (override .env)
    env_map = {
        "APP_PORT": ("port", int),
        "APP_WORKERS": ("workers", int),
        "APP_LOG_LEVEL": ("log_level", str),
        "APP_API_KEY": ("api_key", str),
    }

    for env_key, (cfg_key, caster) in env_map.items():
        if env_key in os.environ:
            config[cfg_key] = caster(os.environ[env_key])

    # 4. CLI overrides
    for item in set:
        if "=" not in item:
            continue

        key, value = item.split("=", 1)

        if key in ("port", "workers"):
            config[key] = int(value)

        elif key == "debug":
            config[key] = value.strip().lower() in (
                "true",
                "1",
                "yes",
                "on",
            )

        else:
            config[key] = value

    config["api_key"] = "****"

    return config

    config = DEFAULTS.copy()

    # YAML
    if os.path.exists("config.development.yaml"):
        with open("config.development.yaml", "r") as f:
            data = yaml.safe_load(f)
            if data:
                config.update(data)

    # .env
    if os.getenv("APP_PORT"):
        config["port"] = int(os.getenv("APP_PORT"))

    if os.getenv("NUM_WORKERS"):
        config["workers"] = int(os.getenv("NUM_WORKERS"))

    if os.getenv("APP_API_KEY"):
        config["api_key"] = os.getenv("APP_API_KEY")

    # OS Environment
    if "APP_PORT" in os.environ:
        config["port"] = int(os.environ["APP_PORT"])

    if "APP_WORKERS" in os.environ:
        config["workers"] = int(os.environ["APP_WORKERS"])

    if "APP_LOG_LEVEL" in os.environ:
        config["log_level"] = os.environ["APP_LOG_LEVEL"]

    if "APP_API_KEY" in os.environ:
        config["api_key"] = os.environ["APP_API_KEY"]

    # CLI Overrides
    for item in set:

        if "=" not in item:
            continue

        key, value = item.split("=", 1)

        if key == "port":
            config["port"] = int(value)

        elif key == "workers":
            config["workers"] = int(value)

        elif key == "debug":
            config["debug"] = to_bool(value)

        else:
            config[key] = value

    config["api_key"] = "****"

    return config