import axios from 'axios';

export const getPrice = () => {
    return {
        type: 'GET_PRICE',
        payload: axios.get(`http://localhost:3000/price`)
    }
}

export const getSentiments = () => {
    return {
        type: 'GET_SENTIMENTS',
        payload: axios.get(`http://localhost:3000/sentiments`)
    }
}