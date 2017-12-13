import * as React from "react";
import * as ReactDOM from "react-dom";

import { TesterPage } from "./tester";
import { SenderPage } from "./im-sender";
import { ReceiverPage } from "./im-receiver";

export type PageProps = {
	report: (message: string) => void;
	check: (message: string) => void;
}

export type PageState = {
	content: "tester" | "sender" | "receiver";
}

export class Page extends React.Component<PageProps, PageState> {
	constructor(props: PageProps) {
		super(props);
		this.state = { content: "tester" };
	}

	render() {
		let content: JSX.Element;

		switch (this.state.content) {
			case "tester":
				content = <TesterPage report={ this.props.report } check={ this.props.check } />;
				break;

			case "sender":
				content = <SenderPage/>;
				break;

			case "receiver":
				content = <ReceiverPage />;
				break;
		}

		return (
			<div id="page">
				<div className="header">
					<h1>spam classification based on word2vec</h1>
					<select onChange={ this.onPageChange.bind(this) }>
						<option value="tester">tester</option>
						<option value="sender">sender</option>
						<option value="receiver">receiver</option>
					</select>
				</div>
				{ content }
			</div>
		);
	}

	private onPageChange(event: React.FormEvent<HTMLSelectElement>) {
		const content = event.currentTarget.value as ("tester" | "sender" | "receiver");

		this.setState({
			content
		});
	}
}

export function render(wrapper: HTMLElement, props: PageProps): void {
	ReactDOM.render(<Page { ...props } />, wrapper);
}