const path = require("path");
const webpack = require("webpack");
const { getIfUtils, removeEmpty } = require("webpack-config-utils");

// variables
const outPath = path.join(__dirname);
const assetsPath = path.join(__dirname, "html");

// plugins
const HtmlWebpackPlugin = require("html-webpack-plugin");

const htmlTemplate = path.join(assetsPath, "index.html");

module.exports = env => {
	const { ifNotProd } = getIfUtils(env || {});
	// get boolean value to use directly in flag configuration;
	const isNotProd = ifNotProd(true, false);

	return {
		devtool: "eval",
		entry: removeEmpty({
			main: path.join(__dirname, "scripts", "bin", "index.js"),
		}),
		output: {
			path: outPath,
			filename: "[name].bundle.js",
			pathinfo: isNotProd,
			publicPath: "/"
		},
		module: {
			noParse: [/\.min\.js$/, /\.bundle\.js$/],
			rules: []
		},
		resolve: {
			extensions: [".ts", ".tsx", ".js"],
			// Fix webpack's default behavior to not load packages with jsnext:main module
			// (jsnext:main directs not usually distributable es6 format, but es6 sources)
			mainFields: ["module", "browser", "main"]
		},
		target: "web",
		plugins: [new HtmlWebpackPlugin({
			template: htmlTemplate,
		})]
	};
};
