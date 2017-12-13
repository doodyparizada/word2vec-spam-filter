server:
	cd server && python app.py

static:
	echo "compile static files"

install:
	pip install -r server/requirements.txt
	echo "install static deps"

download: glove.6B.zip enwiki-20150602-words-frequency.txt
	wget https://github.com/IlyaSemenov/wikipedia-word-frequency/blob/master/results/enwiki-20150602-words-frequency.txt
	wget http://nlp.stanford.edu/data/wordvecs/glove.6B.zip
	unzip glove.6B.zip
