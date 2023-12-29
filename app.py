import logging
import uuid
from functools import lru_cache
from multiprocessing import Pool, Process

from flask import Flask, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/postDatabase"
mongo = PyMongo(app)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)


def write(post_id, data):
    mongo.db.posts.insert_one({"_id": str(post_id), "content": data["content"]})


@app.route("/api/v1/posts/", methods=["POST"])
@limiter.limit("60 per minute")
def create_post():
    try:
        data = request.get_json()

        if data is None or "content" not in data:
            return jsonify({"error": "Content is missing"}), 400
        if not isinstance(data["content"], str):
            return jsonify({"error": "Content should be string"}), 400

        post_id = uuid.uuid4()

        write_process = Process(  # Create a daemonic process for DB write
            target=write, args=(post_id, data), daemon=True
        )
        write_process.start()
        return jsonify({"id": post_id}), 201
    except Exception as e:
        logging.error("An error occurred: %s", e, exc_info=True)
        return jsonify({"error": str(e)}), 500


# This function calculates the number of words and their total length per chunk
def process_chunk(text_chunk):
    words = text_chunk.split()
    num_of_words = len(words)
    tot_word_len = sum(len(word) for word in words)
    return num_of_words, tot_word_len


# This function divide the text into chunks
def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


@app.route("/api/v1/posts/<id>/analysis/", methods=["GET"])
@limiter.limit("100 per minute")
@lru_cache(maxsize=1024)
def get_post(id):
    try:
        post = mongo.db.posts.find_one({"_id": id})

        if post:
            text = post["content"]
            num_of_processors = (
                4  # Should be ideally configured using some kind performance testing.
            )
            pool = Pool(processes=num_of_processors)

            chunk_size = len(text) // num_of_processors
            text_chunks = list(chunks(text, chunk_size))

            results = pool.map(process_chunk, text_chunks)

            num_of_words = sum(x[0] for x in results)
            avg_word_len = sum(x[1] for x in results) / num_of_words

            return jsonify({"num_of_words": num_of_words, "avg_word_len": avg_word_len})
        else:
            return jsonify({"error": "post not found"}), 404
    except Exception as e:
        logging.error("An error occurred: %s", e, exc_info=True)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
