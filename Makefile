server:
	cd server && python app.py

static:
	npm run dev

install:
	pip install -r server/requirements.txt
	cd webclient && npm install

db:
	mkdir -p database
	echo '{}' > database/db.json

download: corpus/glove.6B.zip corpus/enwiki-20150602-words-frequency.txt
	mkdir -p corpus
	wget -P corpus https://github.com/IlyaSemenov/wikipedia-word-frequency/blob/master/results/enwiki-20150602-words-frequency.txt
	wget -p corpus http://nlp.stanford.edu/data/wordvecs/glove.6B.zip
	cd corpus && unzip glove.6B.zip

init: db download install
