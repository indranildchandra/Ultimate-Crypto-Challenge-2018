import axios from 'axios';

export const getPrice = () => {
    return {
        type: 'GET_PRICE',
        payload: axios.get(`http://localhost:3000/price`)
    }
}
