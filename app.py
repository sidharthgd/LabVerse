from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from qa_agent import setup_qa

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

qa = setup_qa()   # This is your process_query function

class QueryRequest(BaseModel):
    query: str

@app.post("/chat")
async def chat_endpoint(req: QueryRequest):
    answer = qa(req.query)
    return {"message": answer}
