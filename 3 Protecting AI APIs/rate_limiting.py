from fastapi import FastAPI, Request, HTTPException, Depends
from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.status import HTTP_429_TOO_MANY_REQUESTS

# Initialize the rate limiter
limiter = Limiter(key_func=get_remote_address)
app = FastAPI()

# Middleware to handle rate limiting
@app.exception_handler(HTTPException)
def rate_limit_handler(request: Request, exc: HTTPException):
    if exc.status_code == HTTP_429_TOO_MANY_REQUESTS:
        return HTTPException(status_code=HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded. Try again later.")
    return exc

@app.get("/")
@limiter.limit("5/minute")  # Allow only 5 requests per minute per IP
async def home(request: Request):
    return {"message": "Welcome to the AI security rate-limited API!"}

@app.get("/secure-data")
@limiter.limit("2/minute")  # More restrictive limit for sensitive endpoints
async def secure_data(request: Request):
    return {"message": "This is a secured endpoint with stricter rate limits."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# uvicorn rate_limiting:app --reload
# http://127.0.0.1:8000/docs