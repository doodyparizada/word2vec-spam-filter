# word2vec-spam-filter

This is a project done during the [Kik](https://github.com/kikinteractive/) hackathon 2017.

In this project we demonstrate a way to classify spam messages on the client while protecting user privacy.

A client generates a "hash" from the message sending it to the server. The server then compares the "hash" to a bank of known reported messages.

The bank of known reported messages is created from spam reports. The server compares a given reported message to the previous bank of reported messages. If the message is similar to a previously reported message, a report count is incremented. Otherwise the message is added to the bank with a count of 1.

A message in the bank of reported messages is considered a spam message once it was reported more than 3 times.

## Corpus downloads
We used 2 datasets for creating sentence vectors:
1. word vectors taken from: https://github.com/stanfordnlp/GloVe
2. word frequencies from: https://github.com/IlyaSemenov/wikipedia-word-frequency/blob/master/results/enwiki-20150602-words-frequency.txt

## Configurable parameters (Hyper-Parameters)
We played around with a few configurations to get the best results for short user messages:

* Confidence Threshold - a number between 0.0 - 1.0 to determine when 2 messages are considered the same
* Distance Function - we used vector dot product
* Normalization - how to deal with words we don't have in our corpus, punctuation marks, non english words
* Vector Size - the longer the vector the higher the accuracy but heavier in memory
* Weight Function - given a word frequency, how to create the vector weights (`the` should weigh less than `camera`)
* Custom Corpus - creating the word vectors and frequencies from real user message data might yield better results
* Random Indices - how many random indices should the client send to the server to mask the original message indices

## Running the code
This project includes a single makefile to help with the initialization, dependency installation and corpus download.
You can invoke a help message by running:

```
make
```

Or you can manually run the server and client apps:

### server
In the `server` directory install the pip dependencies in a `virtualenv`:

```
pip install -r requirements.txt
```

and run the server:
```
python app.py
```

### web client
To use the web client go into the `webclient` directory in your terminal and then:
```
npm install
npm run dev
```

That should install all dependencies and kick start the project, if it all works you should see something like:
 > Project is running at http://localhost:3333/
 > webpack output is served from /

Now load http://localhost:3333/ in your browser

There are 3 different "view modes" which can be switched using the select box at the top right corner of the page.  
The 3 views are:
 * Standalone Tester: A textarea in which one can input a message and then either report it as spam or check whether it is classified as spam.
 * IM Sender: A textarea in which the user can input a message (or select a message from a bunch of existing ones) and then "send" the message to another client.
 * IM Receiver: A view which displays a list of received messages (using the `IM Sender`) and the ability to report each message as spam.
