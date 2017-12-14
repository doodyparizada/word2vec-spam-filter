import * as view from "./page";

const popsicle = require("popsicle");
const shuffle = require("shuffle-array");
const baseUrl = "http://localhost:5000";

const dictionary = {} as { [word: string]: number };
let dictionarySize;
popsicle.request(createGetUrl("/words/list")).then(res => {
	res.body.split("\n").forEach((word, index) => dictionary[word] = index);
	dictionarySize = Object.keys(dictionary).length;
	console.log(`words loaded (count of ${ dictionarySize })`);
});

const main = document.getElementById("main");
view.render(main, {
	report: message => {
		return popsicle.request({
			url: createGetUrl("/spam/report"),
			method: "POST",
			body: {
				message
			}
		});
	},
	check: message => {
		// go to lower case
		message = message.toLowerCase();

		// split message into words
		const words = normalize(message).split(/\s+/);

		// find indexes for words
		const indexes = [] as number[];
		words.forEach(word => {
			if (dictionary[word] !== undefined) {
				indexes.push(dictionary[word]);
			}
		});

		// add random (word) indexes
		const dummyCount = getRandomInt(words.length, words.length * 2);
		const dummys = [] as number[];
		for (let i = 0; i < dummyCount; i++) {
			dummys.push(getRandomInt(0, dictionarySize));
		}

		const ids = indexes.concat(dummys);
		// shuffle indexes
		shuffle(ids);
		return analyze(ids, indexes);
	}
});

function getRandomInt(min, max) {
	min = Math.ceil(min);
	max = Math.floor(max);
	return Math.floor(Math.random() * (max - min)) + min;
}

function normalize(message: string): string {
	return message
		.replace(/\./g, " .")
		.replace(/,/g, " ,")
		.replace(/\?/g, " ?")
		.replace(/\!/g, " !")
		.replace(/\:/g, " :")
		.replace(/'s/g, " 's");
}

function createGetUrl(path: string, arrName?: string, arr?: number[]): string {
	let str = JSON.stringify(arr || []);
	str = str.substring(1, str.length - 1);

	if (str !== "") {
		str = `?${ arrName }=${ str }`;
	}

	return `${ baseUrl }${ path }${ str }`
}

function analyze(indexes: number[], reals: number[]): Promise<{ spam: boolean; confidence: number; }> {
	return popsicle
		.request(createGetUrl("/words/vector", "ids", indexes))
		.use(popsicle.plugins.parse("json"))
		.then(response => {
			let result: Vector = null;

			reals.forEach(index => {
				let vector = new Vector(response.body.words[index].vector);

				if (result === null) {
					result = vector;
				} else {
					result.add(vector);
				}
			});

			return popsicle
				.request(createGetUrl("/spam/detect", "vector", result.toArray()))
				.use(popsicle.plugins.parse("json"))
				.then(response2 => {
					return response2.body;
				});
		});
}

class Vector {
	private readonly values: number[];

	constructor(values: number[]) {
		this.values = values;
	}

	size() {
		return this.values.length;
	}

	add(other: Vector) {
		if (this.size() !== other.size()) {
			throw "error: cannot add vectors of different sizes";
		}

		other.values.forEach((num, index) => this.values[index] += num);
	}

	toArray(): number[] {
		return this.values;
	}
}

console.log("app started");
// hey, what's up? how are you?
