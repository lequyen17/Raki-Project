from fastapi import FastAPI

# Tạo instance ứng dụng (Uvicorn sẽ tìm chính xác biến 'app' này)
app = FastAPI(title="Raki Chat Service API")


@app.get("/")
def read_root():
    return {"message": "Welcome to Raki Chat Service!"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
