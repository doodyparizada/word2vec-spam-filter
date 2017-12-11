from flask import request, Flask, jsonify


app = Flask(__name__)
GLOVE = '../glove.6B.50d.txt'
vectors = {}
vocab = {}
ivocab = {}
WORD_LIST = ''


def init():
    global WORD_LIST, vectors, vocab, ivocab
    words = []

    with open(GLOVE, 'r') as f:
        for line in f:
            vals = line.rstrip().split(' ')
            vectors[vals[0]] = [float(x) for x in vals[1:]]
            words.append(vals[0])

    vocab = {w: idx for idx, w in enumerate(words)}
    ivocab = {idx: w for idx, w in enumerate(words)}
    WORD_LIST += '\n'.join(words)


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
    import random
    vector = request.args['vector'].split(',')
    return jsonify({'spam': bool(random.random() > 0.8), 'confidence': 0.95})


@app.route('/spam/report')
def report_spam():
    data = request.get_json()
    vector = data['vector']
    message = data['message']
    return jsonify({})


if __name__ == '__main__':
    init()
    app.run()
