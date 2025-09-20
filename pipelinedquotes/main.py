from fastapi import FastAPI

app = FastAPI()

def root():
    return {{"status": "ok"}, "200 OK"}

def health_ping():
    @app.get("/health")
    def health():
        return {"status": "ok"}