import React, { Component } from 'react';
import {connect} from 'react-redux'
import {LineChart, Label, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend}  from 'recharts';
import {getPrice, getSentiments} from '../actions/sentimentalActions.js';
import {Tabs, Tab} from 'react-bootstrap';
import {SyncLoader} from 'react-spinners';
import Icon from 'react-icons-kit';
import {caretUp} from 'react-icons-kit/fa/caretUp';
import {caretDown} from 'react-icons-kit/fa/caretDown';
import {square} from 'react-icons-kit/fa/square'
import _ from 'lodash';
const cryptoAttributes = ['low' , 'high', 'open' , 'close'];

let sentimentIcon = null;

class SentimentDetails extends Component {
	constructor(props){
		super(props);
		this.state= {
			time: Date.now(),
			cryptoFeature: 'low',
			cryptoKey: 1
		}
		this.handleSelect = this.handleSelect.bind(this);
	}

	componentDidMount() {
		this.props.getPrice();
		this.props.getSentiments();
		this.interval = setInterval(() => {this.setState({ time: Date.now() }),
		 this.props.getSentiments()}, 60000);
	}

	componentWillUnmount() {
		clearInterval(this.interval);
	}

	handleSelect(key){
		this.setState({cryptoKey: key, cryptoFeature: cryptoAttributes[key-1]})
	}

	render() {
		let priceTrend = [], priceTrendComponent = null;
		let data = _.isEmpty(this.props.sentimentsData)  ? {} :  JSON.parse(this.props.sentimentsData);
		console.log(this.props.sentimentsData, data.general_sentiment);
		if(data.general_sentiment == "Positive"){
			sentimentIcon = (
				<div>
				<h3 style = {{'padding-left': '85%'}}> Sentiment Score: </h3>
				<div  style={{ color: '#009933', float: 'right', paddingRight: '30px'}}> 
				<Icon size = {64} icon ={caretUp}/>
				{data.score}
			</div>
			</div>
			)
		}else if (data.general_sentiment == "Negative"){
			sentimentIcon = (
				<div>
					<h4 style = {{'padding-left': '85%'}}>Sentiment Score: </h4>
				<div  style={{ color: '#e60000', float: 'right', paddingRight: '30px'}}> 
				<Icon size = {64} icon ={caretDown}/>
				{data.score}
			</div>
			</div>
			)
		}

		if(this.props.priceData.length){
		let actualDataType = "actual_" + this.state.cryptoFeature,
		predictedDataType = "predicted_" + this.state.cryptoFeature;
		priceTrend = JSON.parse(this.props.priceData);
			priceTrendComponent = (
				<LineChart width={700} height={500} data={priceTrend} margin={{top: 5, right: 30, left: 20, bottom: 5}}>
       			<XAxis dataKey="timestamp">
				   <Label value="Time" offset={0} position="insideBottom" />
				   </XAxis>
       			<YAxis type="number" domain={['auto', 'auto']} >
				   <Label value="Price ($)" offset={0} position="left" />
				   </YAxis>
       			<CartesianGrid strokeDasharray="3 3"/>
       			<Tooltip/>
       			
				<Line type="monotone" dataKey={actualDataType} stroke="#191966" />
				<Line type="monotone" dataKey={predictedDataType} stroke="#008000" />
				<Legend/>
      		</LineChart>
			)
		}
		else {
			priceTrendComponent = <SyncLoader/>
		}
		return (<div>
			<h2> Bitcoin Trends Portal </h2>
			{sentimentIcon}
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
	priceData : sentimentDetails.priceData,
	sentimentsData: sentimentDetails.sentimentsData
  };
}

const mapDispatchToProps = (dispatch) => {
  return {
      getPrice: () => {
          dispatch(getPrice());
	  },
	  getSentiments : () => {
		  dispatch(getSentiments());
	  }
  }
};

export default connect(mapStateToProps, mapDispatchToProps)(SentimentDetails)
