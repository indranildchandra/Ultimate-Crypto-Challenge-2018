const initialState = {
	isTopInfluencersLoading : false,
	isPopularTweetsLoading: false,
	topInfluencers: [],
	popularTweets: []
}
/**
 * Reducer for home Page
 */
const tweetListReducer = (state = initialState, action) => {
    switch (action.type) {

        case 'LOAD_TOP_INFLUENCERS_PENDING':
            {
                return {
                    ...state,
                    isTopInfluencersLoading: true
                }
            }

        case 'LOAD_TOP_INFLUENCERS_FULFILLED':
            {
                return {
                    ...state,
                    isTopInfluencersLoading: false,
                    topInfluencers: JSON.parse(action.payload.data)
                }
            }

        case 'LOAD_POPULAR_TWEETS_PENDING':
            {
                return { ...state,
                    isPopularTweetsLoading: true
                };
            }

        case 'LOAD_POPULAR_TWEETS_FULFILLED':
            {
                return {
                    ...state,
                    isPopularTweetsLoading: false,
                    popularTweets: JSON.parse(action.payload.data)
                }
            }

        default:
            {
                return state;
            }
    }
}

export default tweetListReducer;
