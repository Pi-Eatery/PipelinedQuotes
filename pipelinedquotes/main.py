from fastapi import FastAPI

def __init__(self, endpoint):
    self.endpoint = "/health"

def root():
    return {{"status": "ok"}, "200 OK"}

def health_ping(self):
    app = FastAPI()
    @app.get(self.endpoint)
    def root():
        return {{"status": "ok"}, "200 OK"}