const initialState = {
    priceData: []
}
/**
 * Reducer for home Page
 */
const sentimentDetailsReducer = (state = initialState, action) => {

    switch (action.type) {

        case 'GET_PRICE_FULFILLED':
            {
                return {
                    ...state,
                   priceData : action.payload.data
                }
            }
    
        default:
            {
                return state;
            }
    }
}

export default sentimentDetailsReducer;
