import json
from math import log

from flask import request, Flask, jsonify
import numpy as np

from model import DB
from generate import generate_matrix, normalize_matrix, normalize_vector
from flask_cors import CORS


app = Flask(__name__)
GLOVE = '../glove.6B.300d.txt'
CORS(app)
FREQ = '../enwiki-20150602-words-frequency.txt'
iweights = {}
vocab = {}
ivocab = {}
WORD_LIST = ''
W_norm = None
EPSILON = 0.99
DEFAULT_WEIGHT = 15


def init():
    """read glove file and generate a word matrix"""
    global W_norm, WORD_LIST, vocab, ivocab, iweights 
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

    max_freq = None
    with open(FREQ, 'r') as f:
        for line in f:
            vals = line.rstrip().split(' ')
            word = vals[0]
            freq = int(vals[1])
            max_freq = max_freq or freq  # the first iteration will set max_freq. The first line is the highest freq
            if word in vocab:
                iweights[vocab[word]] = 0.5 - log(float(freq)/max_freq, 2)  # taken from https://www.wikiwand.com/en/Word_lists_by_frequency
    

def generate_spam_matrix(report_threashold):
    """
    put all known spam vectors in a matrix
    """
    db = read_db()
    word_vectors = [(word, rm.vector)
                    for word, rm in db.reported_messages.items()
                    if rm.reports >= report_threashold]
    return generate_matrix(word_vectors)


def closest_spam(vector, report_threashold=3):
    """given a vector, return the closest spam messages and distance."""
    W, vocab, ivocab = generate_spam_matrix(report_threashold=report_threashold)

    if not vocab:  # means empty db
        return

    vector = normalize_vector(vector)

    dist = np.dot(W, vector.T)

    a = np.argsort(-dist)[:3]  # currently returns generator of 3 most closest
    for x in a:
        print 'found', x, ivocab[x], dist[x]
        yield ivocab[x], float(dist[x])


def read_db():
    with open('db.json', 'r') as f:
        return DB(json.loads(f.read()))


def save_db(db):
    string = json.dumps(db.to_primitive())
    with open('db.json', 'w') as f:
        f.write(string)


@app.route('/words/list')
def word_list():
    """return word list. ordered by indexes."""
    return WORD_LIST


@app.route('/words/vector')
def word_vectors():
    """retrun vectors for the words by given ids."""
    ids = {int(i) for i in request.args['ids'].split(',')}

    return jsonify({'words':
                    {i: {'vector': W_norm[i, :].tolist(), 'weight': iweights.get(i, DEFAULT_WEIGHT)}
                     for i in ids}})


@app.route('/spam/detect')
def detect_spam():
    """the given vector should not be normalized. normalization happens on server."""
    vector = [float(i) for i in request.args['vector'].split(',')]
    results = list(closest_spam(vector))
    if results:
        msg, dist = results[0]
        is_spam = dist > EPSILON
    else:
        dist = 1
        is_spam = False
    return jsonify({'spam': is_spam,
                    'confidence': dist,
                    'meta': dict(results)})


def message_to_vector(message):
    """sums up all known vectors of a given message."""
    vector = np.zeros(W_norm[0, :].shape)
    for term in message.split(' '):  # XXX TOKENIZE message similar to client
        if term in vocab:
            vector += W_norm[vocab[term], :]  # XXX apply weights
    return vector


@app.route('/spam/report', methods=['POST'])
def report_spam():
    """if spam message already exists or is close to a known message add a report count. else add as new entry in db."""
    data = request.get_json()
    reported_message = data['message'].lower()
    vector = message_to_vector(reported_message)

    results = list(closest_spam(vector, 0))
    if results:
        similar_msg, dist = results[0]
    else:
        similar_msg = dist = 0

    db = read_db()
    if dist > EPSILON:
        db.reported_messages[similar_msg].reports += 1
    else:
        db.add_new_message(reported_message, normalize_vector(vector).tolist())

    save_db(db)

    return jsonify({})


if __name__ == '__main__':
    init()
    app.run()
