import React, { Component } from 'react';
import TweetList from '../containers/tweetList'
import SentimentDetails from '../containers/sentimentDetails'
import {Row, Col} from 'react-bootstrap';

export default class App extends Component {
  render() {
    return (
      <Row>
        <Col >
      	<SentimentDetails />   
        </Col>
        <Col>     
      	<TweetList />
        </Col>
      </Row>
    );
  }
}
