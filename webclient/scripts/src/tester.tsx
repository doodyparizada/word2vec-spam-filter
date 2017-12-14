import * as React from "react";

export type TesterPageProps = {
	report: (message: string) => Promise<void>;
	check: (message: string) => Promise<{ spam: boolean; confidence: number; }>;
}

export class TesterPage extends React.Component<TesterPageProps, {}> {
	private textarea: HTMLTextAreaElement;

	render() {
		return (
			<div className="content">
				<textarea placeholder="Enter message here" ref={ el => this.textarea = el }></textarea>
				<div className="actions">
					<button onClick={ this.clear.bind(this) }>Clear</button>
					<button onClick={ this.report.bind(this) }>Report as spam</button>
					<button onClick={ this.check.bind(this) }>Check for spam</button>
				</div>
			</div>
		);
	}

	private clear() {
		this.textarea.value = "";
	}

	private report() {
		this.props.report(this.textarea.value).then(() => alert("message reported"));
	}

	private check() {
		this.props.check(this.textarea.value).then(res => {
			alert(res.spam ? "message is spammy" : "message is ok");
		});
	}
}
