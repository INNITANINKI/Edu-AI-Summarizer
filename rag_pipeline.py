import os
import re
from typing import List
import google.generativeai as genai
from sentence_transformers import SentenceTransformer
import chromadb

# ---------------- GEMINI CONFIG ----------------
GENIE_KEY = os.getenv("GEMINI_API_KEY", "YOUR_API_KEY_HERE")
GENIE_MODEL = "gemini-2.5-flash"

if GENIE_KEY:
    genai.configure(api_key=GENIE_KEY)
else:
    print("⚠️ GEMINI_API_KEY not set. Some functions may not work.")

# ---------------- ChromaDB ----------------
chroma_db_path = "database/chroma"
os.makedirs(chroma_db_path, exist_ok=True)
chroma_client = chromadb.PersistentClient(path=chroma_db_path)
chroma_collection = chroma_client.get_or_create_collection("youtube_docs")

# ---------------- Embedding model ----------------
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# ---------------- CHUNKING ----------------
def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Split text into chunks for embeddings."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunks.append(" ".join(words[i:i + chunk_size]))
    return chunks

# ---------------- STORE IN CHROMA ----------------
def store_in_chroma(doc_id: str, text: str):
    """
    Stores chunks of text in ChromaDB with unique chunk IDs per document.
    Each chunk is tagged with the original doc_id for RAG retrieval.
    """
    chunks = chunk_text(text)
    embeddings = embedder.encode(chunks).tolist()
    chunk_ids = [f"{doc_id}_{i}" for i in range(len(chunks))]

    # Add to Chroma collection
    chroma_collection.add(
        documents=chunks,
        embeddings=embeddings,
        ids=chunk_ids,
        metadatas=[{"doc_id": doc_id}] * len(chunks)
    )
    print(f"✅ Stored {len(chunks)} chunks for {doc_id} in ChromaDB.")

# ---------------- RETRIEVAL ----------------
def retrieve_context_by_doc(query: str, doc_id: str, top_k: int = 3) -> List[str]:
    """
    Retrieve only chunks from the same document ID that are most similar to the query.
    """
    query_embedding = embedder.encode([query]).tolist()[0]
    results = chroma_collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where={"doc_id": doc_id}
    )
    return results["documents"][0] if results and "documents" in results else []

# ---------------- ANSWER FUNCTIONS ----------------
def answer_question_with_mode(question: str, doc_id: str, mode: str = "contextual") -> str:
    """
    mode = "contextual" → uses RAG for given doc_id
    mode = "general" → uses Gemini directly without context
    """
    try:
        model = genai.GenerativeModel(GENIE_MODEL)

        if mode == "contextual":
            context = retrieve_context_by_doc(question, doc_id, top_k=3)
            if not context:
                return "⚠️ No relevant context found in the current document."
            prompt = f"Answer ONLY using the context below:\n\nContext:\n{context}\n\nQuestion:\n{question}"
        else:
            # General AI answer
            prompt = f"Answer the following question generally and clearly:\n\n{question}"

        resp = model.generate_content(prompt)
        return resp.text.strip()

    except Exception as e:
        print(f"[Answer Error] {e}")
        return f"Error: could not answer question ({e})"

# ---------------- SUMMARIZER ----------------
def summarize_text(transcript: str) -> str:
    try:
        model = genai.GenerativeModel(GENIE_MODEL)
        resp = model.generate_content(f"Summarize clearly and concisely:\n\n{transcript}")
        return resp.text.strip()
    except Exception as e:
        print(f"[Summarize Error] {e}")
        return "Error: could not summarize transcript."

# ---------------- QUIZ GENERATOR ----------------
def _parse_quiz_text(quiz_text: str):
    """Parse the quiz text returned by Gemini into structured dicts."""
    quiz = []
    current_q = None
    for line in quiz_text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("Q:"):
            if current_q:
                quiz.append(current_q)
            current_q = {"question": line[2:].strip(), "options": [], "answer": "", "explanation": ""}
        elif re.match(r"^[A-D][\.\)]", line):
            if current_q:
                current_q["options"].append(line)
        elif line.lower().startswith("answer:"):
            if current_q:
                current_q["answer"] = line.split(":", 1)[1].strip()
        elif line.lower().startswith("explanation:"):
            if current_q:
                current_q["explanation"] = line.split(":", 1)[1].strip()
    if current_q:
        quiz.append(current_q)
    return quiz

def generate_quiz(transcript: str, num_questions: int = 5) -> List[dict]:
    """Generate a multiple-choice quiz from transcript using Gemini API."""
    if not GENIE_KEY:
        return [{"question": "Error", "options": ["A) API key missing"], "answer": "A", "explanation": "Set GEMINI_API_KEY"}]

    prompt = f"""
Based on the transcript, create exactly {num_questions} multiple-choice questions with:
- Question
- Four options (A-D)
- Correct answer letter (Answer: A)
- Short explanation

Format:

Q: question text
A) option1
B) option2
C) option3
D) option4
Answer: <letter>
Explanation: text

Transcript:
{transcript}
"""
    try:
        model = genai.GenerativeModel(GENIE_MODEL)
        resp = model.generate_content(prompt)
        quiz_text = resp.text.strip()
        parsed_quiz = _parse_quiz_text(quiz_text)

        # Ensure exact num_questions
        while len(parsed_quiz) < num_questions:
            parsed_quiz.append({
                "question": f"Placeholder question {len(parsed_quiz) + 1}",
                "options": ["A) N/A", "B) N/A", "C) N/A", "D) N/A"],
                "answer": "A",
                "explanation": "Auto-generated placeholder."
            })
        return parsed_quiz[:num_questions]

    except Exception as e:
        print(f"[Quiz Error] {e}")
        return [{"question": "Error generating quiz", "options": ["A) N/A"], "answer": "A", "explanation": str(e)}]
