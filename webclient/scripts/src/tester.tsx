import * as React from "react";

export type TesterPageProps = {
	report: (message: string) => void;
	check: (message: string) => void;
}

export class TesterPage extends React.Component<TesterPageProps, {}> {
	private textarea: HTMLTextAreaElement;

	render() {
		return (
			<div className="content">
				<textarea placeholder="Enter message here" ref={ el => this.textarea = el }></textarea>
				<div className="actions">
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
