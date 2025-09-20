import requests
from fastapi import FastAPI
def health_ping():
    api_enpoint = "/health"