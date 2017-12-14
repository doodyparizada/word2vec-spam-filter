import * as React from "react";

const popsicle = require("popsicle");
const baseUrl = "http://localhost:5000";

export type MessageMeta = { id: number; content: string; isSpam?: boolean; };

export type ReceiverPageProps = {
	report: (message: string) => void;
	check: (message: string) => Promise<{ spam: boolean; confidence: number; }>;
}

export type ReceiverPageState = {
	messages: MessageMeta[];
}

export class ReceiverPage extends React.Component<ReceiverPageProps, ReceiverPageState> {
	private static readonly INTERVAL = 1000;

	private timer: number;

	constructor(props?: any) {
		super(props);

		this.state = {
			messages: []
		};
	}

	componentDidMount() {
		this.timer = setInterval(this.poll.bind(this), ReceiverPage.INTERVAL);
	}

	componentWillUnmount() {
		clearInterval(this.timer);
	}

	render() {
		const messages = this.state.messages.length === 0 ?
			<tr><td>no messages yet</td></tr>
			: this.state.messages.map(message => {
					const clsname = message.isSpam === undefined ? "unknown" : (message.isSpam ? "spam" : "notspam");
					return (
						<tr key={ message.id } className={ clsname }>
							<td> { message.content }</td>
							<td>
								<button onClick={ this.report.bind(this, message) } disabled={ !!message.isSpam }>report</button>
							</td>
						</tr>
					);
				});

		return (
			<div className="content">
				<table className="incoming" cellPadding={ 0 } cellSpacing={ 0 }>
					<tbody>
					{ messages }
					</tbody>
				</table>
			</div>
		);
	}

	private poll() {
		popsicle
			.request(`${ baseUrl }/messages`)
			.use(popsicle.plugins.parse("json"))
			.then(res => {
				if (res.body.message) {
					const id = generateMessageId();

					this.setState({
						messages: [{ id, content: res.body.message }].concat(this.state.messages)
					});

					setTimeout(() => {
						this.props.check(res.body.message).then(res => {
							this.updateMessageState(id, res.spam);
						});
					}, 2500);
				}
			});
	}

	private report(message: MessageMeta) {
		this.props.report(message.content);
		this.updateMessageState(message.id, true);
	}

	private updateMessageState(id: number, spam: boolean) {
		this.setState({
			messages: this.state.messages.map(item => item.id !== id ? item : Object.assign({}, item, { isSpam: spam }))
		});
	}
}

let counter = 0;
function generateMessageId(): number {
	return ++counter;
}
