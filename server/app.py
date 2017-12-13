import json
import sys
from math import log

from flask import request, Flask, jsonify
import numpy as np

from model import DB
from generate import generate_matrix, normalize_matrix, normalize_vector
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

GLOVE = '../glove.6B.50d.txt'
FREQ = '../enwiki-20150602-words-frequency.txt'

iweights = {}
vocab = {}
ivocab = {}
WORD_LIST = ''
W_norm = None
messages = []

EPSILON = 0.95
DEFAULT_WEIGHT = 15


def init():
    """read glove file and generate a word matrix"""
    global W_norm, WORD_LIST, vocab, ivocab, iweights 
    sys.stderr.write('initializing word vectors')
    word_vectors = []
    
    # open and parse word vector file
    with open(GLOVE, 'r') as f:
        for i, line in enumerate(f):
            vals = line.rstrip().split(' ')
            vector = [float(x) for x in vals[1:]]
            word = vals[0]
            word_vectors.append((word, vector))
            if i % 10000 == 0:
                sys.stderr.write('.')
    
    WORD_LIST += '\n'.join(w for w, _ in word_vectors)
    W, vocab, ivocab = generate_matrix(word_vectors)
    W_norm = normalize_matrix(W)

    sys.stderr.write('\ninitializing word weights')
    max_freq = None
    with open(FREQ, 'r') as f:
        for i, line in enumerate(f):
            vals = line.rstrip().split(' ')
            word = vals[0]
            freq = int(vals[1])
            max_freq = max_freq or freq  # the first iteration will set max_freq. The first line is the highest freq
            if word in vocab:
                iweights[vocab[word]] = freq_to_weight(freq, max_freq)
            if i % 10000 == 0:
                sys.stderr.write('.')

    sys.stderr.write('\ndone!\n')


def get_vector(idx):
    """return the weighted vector for an index."""
    return (W_norm[idx, :] * iweights.get(idx, DEFAULT_WEIGHT))


def freq_to_weight(freq, max_freq):
    """calculate a vector weight for a frequency."""
    # taken from https://www.wikiwand.com/en/Word_lists_by_frequency
    return 0.5 - log(float(freq)/max_freq, 2)

    
def generate_spam_matrix(report_threashold):
    """
    put all known spam vectors in a matrix
    """
    db = DB.load()
    word_vectors = [(word, rm.vector)
                    for word, rm in db.reported_messages.items()
                    if rm.reports >= report_threashold]
    return generate_matrix(word_vectors)


def closest_spam(vector, report_threashold=3):
    """given a vector, return the closest spam messages and distance."""
    W, vocab, ivocab = generate_spam_matrix(report_threashold=report_threashold)

    if not vocab:  # means empty db
        return '', 0

    vector = normalize_vector(vector)

    dist = np.dot(W, vector.T)

    a = np.argsort(-dist)[:1]  # currently returns generator of 3 most closest
    for x in a:
        return ivocab[x], float(dist[x])

    return '', 0

def tokenize_message(message):
    """return a list of normalized words."""
    return (message
            .lower()
            .replace(".", " .")
            .replace(",", " ,")
            .replace("?", " ?")
            .replace("!", " !")
            .replace(":", " :")
            .replace("'s", " 's")
            .split())


def message_to_vector(message):
    """sums up all known vectors of a given message."""
    vector = np.zeros(W_norm[0, :].shape)
    for term in tokenize_message(message):
        if term in vocab:
            vector += get_vector(vocab[term])
    return vector


@app.route('/words/list')
def word_list():
    """return word list. ordered by indexes."""
    return WORD_LIST


@app.route('/words/vector')
def word_vectors():
    """retrun vectors for the words by given ids."""
    ids = {int(i) for i in request.args['ids'].split(',')}

    return jsonify({'words':
                    {i: {'vector': get_vector(i).tolist()}
                     for i in ids}})


@app.route('/spam/detect')
def detect_spam():
    """the given vector should not be normalized. normalization happens on server."""
    vector = [float(i) for i in request.args['vector'].split(',')]
    msg, dist = closest_spam(vector)
    is_spam = dist > EPSILON
    return jsonify({'spam': is_spam,
                    'confidence': dist,
                    'meta': msg})


@app.route('/spam/report', methods=['POST'])
def report_spam():
    """if spam message already exists or is close to a known message add a report count. else add as new entry in db."""
    data = request.get_json()
    reported_message = data['message']
    vector = message_to_vector(reported_message)

    similar_msg, dist = closest_spam(vector, 0)

    db = DB.load()
    if dist > EPSILON:
        db.reported_messages[similar_msg].reports += 1
    else:
        db.add_new_message(reported_message, normalize_vector(vector).tolist())

    db.save()
    return jsonify({})

@app.route('/messages', methods=['POST', 'GET'])
def message_handler():
    global messages
    if request.method == 'POST':
        messages.append(request.get_json()['message'])
        return jsonify({})
    else:
        if messages:
            return jsonify({'message': messages.pop(0)})
        return jsonify({})


if __name__ == '__main__':
    init()
    app.run()
