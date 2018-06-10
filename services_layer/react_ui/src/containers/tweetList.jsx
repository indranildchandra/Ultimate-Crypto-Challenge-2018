import React, {Component} from 'react'
import {connect} from 'react-redux'
import { Table } from "react-bootstrap";
import {FadeLoader} from 'react-spinners';
import {loadPopularTweets, loadTopInfluencers} from '../actions/tweetListActions.js';

class TweetList extends Component {
  componentWillMount(){
    if(!this.props.popularTweets.length){
      this.props.loadPopularTweets();
    }

    if(!this.props.topInfluencers.length){
      this.props.loadTopInfluencers();
    }
  }

  componentDidMount() {
		this.interval = setInterval(() => {this.setState({ time: Date.now() }),
    this.props.loadPopularTweets(), this.props.loadTopInfluencers()}, 30000);
	}

	componentWillUnmount() {
		clearInterval(this.interval);
	}
  
  render() {
    let popularTweetsData =[], topInfluencersData =[];

    if(this.props.isPopularTweetsLoading){
        popularTweetsData = <FadeLoader style = {{'margin-top': '100px'}}/>
    }else{
      const {popularTweets} = this.props;
      let tweetBody =[];
      popularTweets.forEach(tweet => {
        tweetBody.push(<tr>
          <td>
          {tweet.popular_tweet_content}
          </td>
          </tr>)
      })

      popularTweetsData = (
        <Table>
          <thead>
            <tr>
              <th>
            Influential Tweets
              </th>
            </tr>
          </thead>
          <tbody>
            {tweetBody}
            </tbody>
        </Table>
      )
    }

    if(!this.props.isTopInfluencersLoading){
      const {topInfluencers }= this.props;
      let influencerBody = [];
      for(let i =0; i<topInfluencers.length;i++){
        const link = "https://twitter.com/" + topInfluencers[i].twitter_handle;
        influencerBody.push(<tr>
          <td>
            {i+1}
            </td>
          <td>
          <a href = {link}>{topInfluencers[i].name} - {topInfluencers[i].twitter_handle}</a>
          </td>
          </tr>)
      }
      topInfluencersData = (
        <Table>
          <thead>
            <tr>
              <th>
                #
              </th>
              <th>
            Top 5 Influential People
              </th>
            </tr>
          </thead>
          <tbody>
            {influencerBody}
            </tbody>
        </Table>
      )

    }

    return (
      <div>
        <div className = 'popularTweetData'>
        {topInfluencersData}
        </div>
        <div className = 'popularTweetData'>
        {popularTweetsData}
        </div>
      </div>
    );
  }
}

const mapStateToProps = ({tweetList}) => {
  return {
    isPopularTweetsLoading: tweetList.isPopularTweetsLoading,
    isTopInfluencersLoading: tweetList.isTopInfluencersLoading,
    topInfluencers: tweetList.topInfluencers,
    popularTweets: tweetList.popularTweets
  };
}

const mapDispatchToProps = (dispatch) => {
  return {
      loadPopularTweets: () => {
          dispatch(loadPopularTweets());
      },

      loadTopInfluencers: () => {
          dispatch(loadTopInfluencers());
      }
  }
};


export default connect(mapStateToProps, mapDispatchToProps)(TweetList)
