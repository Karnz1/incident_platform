from fastapi import FastAPI

app = FastAPI()


@app.post("/incidents")
def create_incident():
    return "incident created"


@app.get("/incidents")
def get_all_incidents():
    return "ALL incidents"


@app.get("/incidents/{id}")
def get_incident(id: str):
    return "return specific incident"

@app.patch("/incident/{id}")
def update_incident(id: str):
    return "updated incident"

@app.delete("/incidents/{id}")
def delete_incident(id: str):
    return "deleted incident"

@app.get("/ready")
def dep_ready():
    return "dependencies check"


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/metrics")
def get_metrics():
    return "return prometheus metrics"





