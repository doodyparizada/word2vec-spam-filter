import numpy as np


def normalize_vector(vector):
    vector = np.array(vector)
    vec_norm = np.zeros(vector.shape)
    d = (np.sum(vector ** 2,) ** (0.5))
    vec_norm = (vector.T / d).T
    return vec_norm


# XXX todo see if we can unite vector and matrix normalization
def normalize_matrix(W):
    # normalize each word vector to unit variance
    W_norm = np.zeros(W.shape)
    d = (np.sum(W ** 2, 1) ** (0.5))
    W_norm = (W.T / d).T
    return W_norm


def generate_matrix(word_vectors):
    """given a list of word,vector pairs generate matrix and vocab dicts""" 
    vectors = dict(word_vectors)
    words = [w for w, _ in word_vectors]

    vocab = {w: idx for idx, w in enumerate(words)}
    ivocab = {idx: w for idx, w in enumerate(words)}
        
    vocab_size = len(vectors)
    vector_dim = len(vectors.values()[0]) if vectors else 0
    W = np.zeros((vocab_size, vector_dim))
    for word, v in vectors.items():
        W[vocab[word], :] = v
    return W, vocab, ivocab
