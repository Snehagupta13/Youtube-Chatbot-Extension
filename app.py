from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from pipeline import build_main_chain, generate_summary

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    video_id: str
    question: str = None  # Optional for summarize endpoint

@app.get("/")
def read_root():
    return {"message": "YouTube Chatbot is running!"}

@app.post("/ask")
async def ask_video_question(request: QueryRequest):
    if not request.question:
        raise HTTPException(status_code=400, detail="Question is required")
    
    chain = build_main_chain(request.video_id)
    if chain is None:
        raise HTTPException(status_code=404, detail="No transcript available")
    
    try:
        answer = chain.invoke(request.question)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/summarize")
async def summarize_video(request: QueryRequest):
    try:
        summary = await generate_summary(request.video_id)  # Note the await here
        if not summary:
            raise HTTPException(status_code=404, detail="No transcript available")
        return {"answer": summary}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating summary: {str(e)}"
        )