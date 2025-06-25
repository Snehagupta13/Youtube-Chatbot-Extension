import os
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq

load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

def build_main_chain(video_id):
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=["en"])
        transcript = " ".join(chunk["text"] for chunk in transcript_list)
    except TranscriptsDisabled:
        return None

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.create_documents([transcript])
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vector_store = FAISS.from_documents(chunks, embeddings)
    retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 4})

    llm = ChatGroq(api_key=groq_api_key, model_name="llama3-8b-8192")
    prompt = PromptTemplate(
        template="""
        You are a helpful assistant that answers questions about YouTube videos.
        Use only the following context from the video transcript to answer the question.
        If the context is insufficient, respond with "I don't know."

        Context: {context}
        Question: {question}
        Answer: """,
        input_variables=["context", "question"]
    )

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    chain = RunnableParallel({
        "context": retriever | RunnableLambda(format_docs),
        "question": RunnablePassthrough()
    }) | prompt | llm | StrOutputParser()

    return chain
# ... (keep previous imports and build_main_chain function)

async def generate_summary(video_id):
    try:
        # Get transcript
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=["en"])
        full_transcript = " ".join(chunk["text"] for chunk in transcript_list)
        
        # Split into chunks (for long videos)
        splitter = RecursiveCharacterTextSplitter(chunk_size=4000, chunk_overlap=200)
        chunks = splitter.create_documents([full_transcript])
        
        # Initialize LLM
        llm = ChatGroq(api_key=groq_api_key, model_name="llama3-8b-8192", temperature=0.3)
        
        # Map-reduce summarization
        map_prompt = PromptTemplate.from_template(
            "Summarize this portion of a YouTube video transcript:\n\n{text}\n\nSummary:"
        )
        map_chain = map_prompt | llm | StrOutputParser()
        
        reduce_prompt = PromptTemplate.from_template(
            "Combine these summaries into one coherent summary of the entire video:\n\n{text}\n\nFinal Summary:"
        )
        reduce_chain = reduce_prompt | llm | StrOutputParser()
        
        # Process chunks in parallel
        map_results = []
        for chunk in chunks:
            map_results.append(await map_chain.ainvoke({"text": chunk.page_content}))
        
        # Combine results
        combined = "\n\n".join(map_results)
        final_summary = await reduce_chain.ainvoke({"text": combined})
        
        return final_summary
        
    except TranscriptsDisabled:
        return None
    except Exception as e:
        raise e