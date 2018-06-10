import React, { Component } from 'react';
import {connect} from 'react-redux'
import {LineChart, Label, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend}  from 'recharts';
import {getPrice} from '../actions/sentimentalActions.js';
import {Tabs, Tab} from 'react-bootstrap';
import {SyncLoader} from 'react-spinners';
import Icon from 'react-icons-kit';
import {caretUp} from 'react-icons-kit/fa/caretUp';
import {caretDown} from 'react-icons-kit/fa/caretDown';
import {square} from 'react-icons-kit/fa/square'
const cryptoAttributes = ['low' , 'high', 'open' , 'close'];

class SentimentDetails extends Component {
	constructor(props){
		super(props);
		this.state= {
			time: Date.now(),
			cryptoFeature: 'Low',
			cryptoKey: 1
		}
		this.handleSelect = this.handleSelect.bind(this);
	}

	componentDidMount() {
		this.interval = setInterval(() => {this.setState({ time: Date.now() }),
		this.props.getPrice()}, 10000);
	}

	componentWillUnmount() {
		clearInterval(this.interval);
	}

	handleSelect(key){
		this.setState({cryptoKey: key, cryptoFeature: cryptoAttributes[key-1]})
	}

	render() {
		let priceTrend = [], priceTrendComponent = null;

		// if(true){
		// 	sentimentIcon = (
		// 		<div  style={{ color: '#009933', float: 'right'}}> 
		// 		<Icon size = {64} icon ={caretUp}/>
		// 	</div>
		// 	)
		// }

		if(this.props.priceData.length){
		let dataType = "i" + this.state.cryptoFeature;
		priceTrend = JSON.parse(this.props.priceData);
			priceTrendComponent = (
				<LineChart width={600} height={300} data={priceTrend} margin={{top: 5, right: 30, left: 20, bottom: 5}}>
       			<XAxis dataKey="timestamp">
				   <Label value="Time" offset={0} position="insideBottom" />
				   </XAxis>
       			<YAxis type="number" domain={['auto', 'auto']} >
				   <Label value="Price ($)" offset={0} position="left" />
				   </YAxis>
       			<CartesianGrid strokeDasharray="3 3"/>
       			<Tooltip/>
       			
				<Line type="monotone" dataKey={dataType} stroke="#191966" />
				<Line type="monotone" dataKey={this.state.cryptoFeature} stroke="#008000" />
				<Legend/>
      		</LineChart>
			)
		}
		else {
			priceTrendComponent = <SyncLoader/>
		}
		return (<div>
			<h2> Bitcoin Price Trend </h2>
			{/* {sentimentIcon} */}
				<Tabs defaultActiveKey={1} activeKey={this.state.cryptoKey} onSelect = {this.handleSelect} id="uncontrolled-tab-example">
  					<Tab eventKey={1} title="Low">
  					</Tab>
  					<Tab eventKey={2} title="High">
  					</Tab>
  					<Tab eventKey={3} title="Open">
  					</Tab>
					<Tab eventKey={4} title="Close">
  					</Tab>
					  </Tabs>
			{priceTrendComponent}
			</div>);
	}
}

const mapStateToProps = ({sentimentDetails}) => {
  return {
    priceData : sentimentDetails.priceData
  };
}

const mapDispatchToProps = (dispatch) => {
  return {
      getPrice: () => {
          dispatch(getPrice());
      }
  }
};

export default connect(mapStateToProps, mapDispatchToProps)(SentimentDetails)
