from flask import request, Flask, jsonify
import json
import numpy as np


app = Flask(__name__)
GLOVE = '../glove.6B.50d.txt'
vectors = {}
vocab = {}
ivocab = {}
WORD_LIST = ''
W_norm = None


def init():
    global W_norm, WORD_LIST, vectors, vocab, ivocab
    words = []
    
    # open and parse word vector file
    with open(GLOVE, 'r') as f:
        for line in f:
            vals = line.rstrip().split(' ')
            # word 0.1 0.1 0.1 0.1 ...
            vectors[vals[0]] = [float(x) for x in vals[1:]]
            words.append(vals[0])

    vocab = {w: idx for idx, w in enumerate(words)}
    ivocab = {idx: w for idx, w in enumerate(words)}
    WORD_LIST += '\n'.join(words)


def generate_spam_matrix():
    """
    put all known spam vectors in a matrix
    """
    # create and normalize the huge word matrix
    db = read_db()
    vectors = {}
    words = db.keys()
    for word, val in db:
        if val['reports'] < 3:
            continue
        vectors[word] = [float(x) for x in val['vector']]

    vocab = {w: idx for idx, w in enumerate(words)}
    ivocab = {idx: w for idx, w in enumerate(words)}
        
    vocab_size = len(vectors)
    vector_dim = len(vectors.values()[0])
    W = np.zeros((vocab_size, vector_dim))
    for word, v in vectors.items():
        W[vocab[word], :] = v
    return W, vocab, ivocab


def normalize_vector(vector):
    vec_norm = np.zeros(vector.shape)
    d = (np.sum(vector ** 2,) ** (0.5))
    vec_norm = (vector.T / d).T
    return vec_norm


def closest_spam(vector):
    """given a vector, return the closest spam messages and distance."""
    W, vocab, ivocab = generate_spam_matrix()
    
    vector = normalize_vector(np.array(vector))

    dist = np.dot(W, vector.T)

    a = np.argsort(-dist)[:3]
    for x in a:
        yield ivocab[x], dist[x]


def read_db():
    """
    example:
    {
      'message 1': {'reports': 3, 'vector': [0.1, 0.2, ...]},
      'message 2': {'reports': 3, 'vector': [0.1, 0.2, ...]},
    }
    """
    return json.load('db.json')


def save_db(db):
    json.dump(db)


@app.route('/words/list')
def word_list():
    """return word list. ordered by indexes."""
    return WORD_LIST


@app.route('/words/vector')
def word_vectors():
    """retrun vectors for the words by given ids.
    
    when there is no vector for a given word index, it is skipped.
    """
    ids = [int(i) for i in request.args['ids'].split(',')]

    return jsonify({'words':
                    {i: {'vector': vectors[ivocab[i]]}
                     for i in ids
                     if i in ivocab and ivocab[i] in vectors}})


@app.route('/spam/detect')
def detect_spam():
    """the given vector should not be normalized. normalization happens on server."""
    vector = [int(i) for i in request.args['vector'].split(',')]
    results = list(closest_spam(vector))
    if results:
        msg, dist = results[0]
        return jsonify({'spam': dist > 0.9, 'confidence': dist, 'meta': dict(results)})
    return jsonify({'spam': False, 'confidence': 1, 'meta': {}})


@app.route('/spam/report')
def report_spam():
    """if spam message already exists or is close to a known message add a report count. else add as new entry in db."""
    data = request.get_json()
    vector = data['vector']
    message = data['message']  # XXX maybe calculate this myself?

    results = list(closest_spam(vector))
    if results:
        msg, dist = results[0]
    else:
        msg = dist = 0

    db = read_db()
    if dist > 0.9:
        db[msg]['reports'] += 1
    else:
        db[message] = {'reports': 1, 'vector': normalize_vector(vector)}

    save_db(db)

    return jsonify({})


if __name__ == '__main__':
    init()
    app.run()
