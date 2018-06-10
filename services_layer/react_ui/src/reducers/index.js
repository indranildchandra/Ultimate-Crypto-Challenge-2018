import { combineReducers } from 'redux';
import tweetListReducer from './tweetListReducer';
import sentimentDetailsReducer from './sentimentDetailsReducer';

const rootReducer = combineReducers({
	tweetList: tweetListReducer,
	sentimentDetails: sentimentDetailsReducer
});

export default rootReducer;
