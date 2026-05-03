# 🎓 Edu AI Summarizer

An AI-powered learning assistant that summarizes YouTube videos and documents, answers questions using RAG (Retrieval-Augmented Generation), and generates quizzes for effective learning.

---

## 🚀 Features

* 🎥 **YouTube Video Summarization**

  * Extracts transcripts using YouTube Transcript API
  * Falls back to Whisper (speech-to-text) if transcript is unavailable
  * Generates concise summaries using Gemini API

* 📄 **Document Summarization**

  * Supports PDF, PPTX, DOCX, and TXT files
  * Extracts and summarizes large content efficiently

* ❓ **RAG-Based Doubt Solving**

  * Uses Retrieval-Augmented Generation (RAG)
  * Stores document chunks in ChromaDB
  * Retrieves relevant context before generating answers

* 🧠 **Dual Answer Modes**

  * Context-based answers (RAG)
  * General AI answers (Gemini)

* 📝 **Quiz Generation**

  * Automatically generates MCQs from content
  * Includes answers and explanations

* 💾 **Database Integration**

  * SQLite for storing transcripts, summaries, and FAQs
  * ChromaDB for vector-based retrieval

* ⚡ **Efficient Processing**

  * Sentence Transformers for embeddings
  * Chunking strategy for large text handling

* 🌐 **Interactive UI**

  * Built with Streamlit for a clean and user-friendly interface

---

## 🛠️ Tech Stack

* **Frontend:** Streamlit
* **Backend:** Python
* **AI Model:** Google Gemini API
* **RAG Pipeline:** ChromaDB + Sentence Transformers
* **Speech-to-Text:** Faster-Whisper
* **YouTube Processing:** YouTube Transcript API, yt-dlp
* **Database:** SQLite
* **Libraries:** pdfplumber, python-docx, python-pptx

---

## 📁 Project Structure

```bash
edu_ai_project/
│── app.py                  # Main Streamlit app
│── db.py                   # SQLite + ChromaDB setup
│── rag_pipeline.py         # RAG logic (chunking, embeddings, retrieval)
│── transcript.py           # YouTube transcript extraction
│── requirements.txt
│── database/
│   ├── videos.db
│   └── chroma/
│── temp/                   # Temporary audio storage
```

---

###  Clone Repository

```bash
git clone https://github.com/INNITANINKI/Edu-AI-Summarizer.git
cd Edu-AI-Summarizer
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Application

```bash
streamlit run app.py
```

---

## 🔄 How It Works (Architecture)

1. **Input**

   * YouTube URL OR Document upload

2. **Text Extraction**

   * YouTube → Transcript API / Whisper
   * Documents → File parsers

3. **Processing**

   * Text chunking
   * Embedding using Sentence Transformers

4. **Storage**

   * Chunks stored in ChromaDB
   * Metadata stored in SQLite

5. **RAG Pipeline**

   * Query → Retrieve relevant chunks
   * Pass context + question to Gemini

6. **Output**

   * Summary / Answer / Quiz

---

## 📊 Key Concepts Used

* Retrieval-Augmented Generation (RAG)
* Vector Databases (ChromaDB)
* Embeddings (Sentence Transformers)
* LLM Integration (Gemini API)
* NLP & Text Processing

---

## 🎯 Use Cases

* 📚 Students summarizing lectures
* 📝 Exam preparation
* 🔍 Quick content understanding



