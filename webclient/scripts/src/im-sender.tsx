import * as React from "react";

const popsicle = require("popsicle");
const baseUrl = "http://localhost:5000";

function createGetUrl(path: string): string {
	return `${ baseUrl }${ path }`;
}

export class SenderPage extends React.Component<{}, {}> {
	private textarea: HTMLTextAreaElement;

	render() {
		return (
			<div className="content">
				<div id="examples">
					<ul onClick={ this.onClickExample.bind(this) }>
						<li>Hi are you looking for a sexy cool woman to spend time ,with well I,m lookin for a gentleman who still khowns how to treat a lady, I am here to u.http . G.lovendate.pw code: 605</li>
						<li>I offer you an exchange, you free register on my site http://rachelmel.pro Confirmation email and show me the screenshot.  After that I'll send you my nude pics</li>
						<li>Hi, do I know u? you just showed up in my kik hmm.. my friends warned me that there are many fake accounts and bots here, no offense, are u a real person? If you are a real person, you won't have any trouble liking my pic, will you;)? the one where I'm wearing a white swimming suit. This way I'll be convinced that you are real</li>
						<li>Whats going on Nitzan, Its me Doody from the party last night</li>
					</ul>
				</div>
				<textarea placeholder="Enter message here" ref={ el => this.textarea = el }></textarea>
				<div className="actions">
					<button onClick={ this.send.bind(this) }>Send Message</button>
				</div>
			</div>
		);
	}

	private send() {
		popsicle.request({
			url: createGetUrl("/messages"),
			method: "POST",
			body: {
				message: this.textarea.value
			}
		}).then(res => console.log("message sent"));
	}

	private onClickExample(event: React.MouseEvent<HTMLUListElement>) {
		this.textarea.value = (event.target as HTMLLIElement).textContent;
	}
}
