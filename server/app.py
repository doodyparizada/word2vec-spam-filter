import json

from flask import request, Flask, jsonify
import numpy as np

from model import DB
from generate import generate_matrix, normalize_matrix, normalize_vector


app = Flask(__name__)
GLOVE = '../glove.6B.50d.txt'
vocab = {}
ivocab = {}
WORD_LIST = ''
W_norm = None


def init():
    """read glove file and generate a word matrix"""
    global W_norm, WORD_LIST, vocab, ivocab
    word_vectors = []
    
    # open and parse word vector file
    with open(GLOVE, 'r') as f:
        for line in f:
            vals = line.rstrip().split(' ')
            vector = [float(x) for x in vals[1:]]
            word = vals[0]
            word_vectors.append((word, vector))

    WORD_LIST += '\n'.join(w for w, _ in word_vectors)
    W, vocab, ivocab = generate_matrix(word_vectors)
    W_norm = normalize_matrix(W)


def generate_spam_matrix():
    """
    put all known spam vectors in a matrix
    """
    db = read_db()
    word_vectors = [(word, rm.vector)
                    for word, rm in db.reported_messages.items()
                    if rm.reports >= 3]
    return generate_matrix(word_vectors)


def closest_spam(vector):
    """given a vector, return the closest spam messages and distance."""
    W, vocab, ivocab = generate_spam_matrix()
    
    vector = normalize_vector(np.array(vector))

    dist = np.dot(W, vector.T)

    a = np.argsort(-dist)[:3]  # currently returns generator of 3 most closest
    for x in a:
        yield ivocab[x], dist[x]


def read_db():
    return DB(json.load('db.json'))


def save_db(db):
    json.dump(db.to_primitive(), 'db.json')


@app.route('/words/list')
def word_list():
    """return word list. ordered by indexes."""
    return WORD_LIST


@app.route('/words/vector')
def word_vectors():
    """retrun vectors for the words by given ids."""
    ids = [int(i) for i in request.args['ids'].split(',')]

    return jsonify({'words':
                    {i: {'vector': W_norm[i, :]}
                     for i in ids}})


@app.route('/spam/detect')
def detect_spam():
    """the given vector should not be normalized. normalization happens on server."""
    vector = [int(i) for i in request.args['vector'].split(',')]
    results = list(closest_spam(vector))
    if results:
        msg, dist = results[0]
        is_spam = dist > 0.9
    else:
        dist = 1
        is_spam = False
    return jsonify({'spam': is_spam,
                    'confidence': dist,
                    'meta': dict(results)})


def message_to_vector(message):
    """sums up all known vectors of a given message."""
    vector = np.zeors(W_norm[0, :].shape)
    for term in message.split(' '):
        if term in vocab:
            vector += W_norm[vocab[term], :]
    return vector


@app.route('/test/calc_vector')
def calc_vector():
    ids = [int(i) for i in request.args['ids'].split(',')]

    vector = np.zeors(W_norm[0, :].shape)
    if i in ids:
        vector += W_norm[i, :]

    return jsonify({'vector': normalize_vector(vector).tolist()})


@app.route('/spam/report')
def report_spam():
    """if spam message already exists or is close to a known message add a report count. else add as new entry in db."""
    data = request.get_json()
    vector = data['vector']
    reported_message = data['message']
    print('calculate vs given', vector == message_to_vector(reported_message))

    results = list(closest_spam(vector))
    if results:
        similar_msg, dist = results[0]
    else:
        similar_msg = dist = 0

    db = read_db()
    if dist > 0.9:
        db.reported_messages[similar_msg].reports += 1
    else:
        db.add_new_message(reported_message, normalize_vector(vector).tolist())

    save_db(db)

    return jsonify({})


if __name__ == '__main__':
    init()
    app.run()
