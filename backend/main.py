from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Welcome to the EPL Predictor API"}


@app.get("/predict")
def predict():
    # Replace with actual prediction logic
    return {"prediction": "Sample prediction"}
