from flask import request, Flask, jsonify


app = Flask(__name__)

def init():
    """
    read the word vectors file.
    init connection to DB.
    """


@app.route('/words/list')
def word_list():
    return jsonify({'words': ['a', 'abba', 'apple', 'zebra']})


@app.route('/words/vector')
def word_vectors():
    ids = [i for i in request.args['ids'].split(',')]
    return jsonify({'words': {i: {'vector': [0.1]*10} for i in ids}})


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

