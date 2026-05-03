# import os
# import sqlite3
# import json
# import chromadb

# # ------------------ SQLITE ------------------
# def init_sqlite(db_path="database/videos.db"):
#     os.makedirs(os.path.dirname(db_path), exist_ok=True)
#     conn = sqlite3.connect(db_path, check_same_thread=False)
#     cursor = conn.cursor()
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS videos (
#             video_id TEXT PRIMARY KEY,
#             title TEXT,
#             transcript TEXT,
#             summary TEXT,
#             quiz TEXT,
#             faqs TEXT
#         )
#     """)
#     conn.commit()
#     return conn


# def load_faqs(conn, video_id):
#     cursor = conn.cursor()
#     cursor.execute("SELECT faqs FROM videos WHERE video_id=?", (video_id,))
#     row = cursor.fetchone()
#     return json.loads(row[0]) if row and row[0] else []


# def save_faq(conn, video_id, question, answer):
#     faqs = load_faqs(conn, video_id)
#     faqs.append({"question": question, "answer": answer})
#     cursor = conn.cursor()
#     cursor.execute("UPDATE videos SET faqs=? WHERE video_id=?", (json.dumps(faqs), video_id))
#     conn.commit()


# # ------------------ CHROMA ------------------
# chroma_db_path = "database/chroma"
# os.makedirs(chroma_db_path, exist_ok=True)
# chroma_client = chromadb.PersistentClient(path=chroma_db_path)

# try:
#     chroma_collection = chroma_client.get_collection("youtube_videos")
# except ValueError:
#     chroma_collection = chroma_client.create_collection("youtube_videos")
import os
import sqlite3
import json
import chromadb
from chromadb.errors import NotFoundError

# ------------------ SQLITE ------------------
def init_sqlite(db_path="database/videos.db"):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS videos (
            video_id TEXT PRIMARY KEY,
            title TEXT,
            transcript TEXT,
            summary TEXT,
            quiz TEXT,
            faqs TEXT
        )
    """)
    conn.commit()
    return conn


def load_faqs(conn, video_id):
    cursor = conn.cursor()
    cursor.execute("SELECT faqs FROM videos WHERE video_id=?", (video_id,))
    row = cursor.fetchone()
    return json.loads(row[0]) if row and row[0] else []


def save_faq(conn, video_id, question, answer):
    faqs = load_faqs(conn, video_id)
    faqs.append({"question": question, "answer": answer})
    cursor = conn.cursor()
    cursor.execute("UPDATE videos SET faqs=? WHERE video_id=?", (json.dumps(faqs), video_id))
    conn.commit()


# ------------------ CHROMA ------------------
chroma_db_path = "database/chroma"
os.makedirs(chroma_db_path, exist_ok=True)
chroma_client = chromadb.PersistentClient(path=chroma_db_path)

COLLECTION_NAME = "youtube_videos"

try:
    chroma_collection = chroma_client.get_collection(COLLECTION_NAME)
except NotFoundError:
    chroma_collection = chroma_client.create_collection(name=COLLECTION_NAME)

print(f"✅ ChromaDB collection ready: {COLLECTION_NAME}")
