import * as React from "react";
import * as ReactDOM from "react-dom";

const popsicle = require("popsicle");

/*export class MessageInput extends React.Component<{}, {}> {
	render() {
		return (
			<textarea></textarea>
		);
	}
}*/

export type PageProps = {
	report: (message: string) => void;
	check: (message: string) => void;
}

export class Page extends React.Component<PageProps, {}> {
	private textarea: HTMLTextAreaElement;

	render() {
		return (
			<div id="page">
				<h1>spam classification based on word2vec</h1>
				<textarea placeholder="Enter message here" ref={ el => this.textarea = el }></textarea>
				<div>
					<button onClick={ this.report.bind(this) }>Report as spam</button>
					<button onClick={ this.check.bind(this) }>Check for spam</button>
				</div>
			</div>
		);
	}

	private report() {
		this.props.report(this.textarea.value);
	}

	private check() {
		this.props.check(this.textarea.value);
	}
}

export function render(wrapper: HTMLElement, props: PageProps): void {
	ReactDOM.render(<Page { ...props } />, wrapper);
}
