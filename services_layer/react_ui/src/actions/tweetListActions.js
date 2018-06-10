import axios from 'axios';

export const loadPopularTweets = () => {
    return {
        type: 'LOAD_POPULAR_TWEETS',
        payload: axios.get(`http://localhost:3000/topTweets`)
    }
}

export const loadTopInfluencers = (data) => {
    return {
        type: 'LOAD_TOP_INFLUENCERS',
        payload: axios.get(`http://localhost:3000/popularInfluencers`)
    }
}
