const initialState = {
    priceData: [],
    sentimentsData: {}
}
/**
 * Reducer for home Page
 */
const sentimentDetailsReducer = (state = initialState, action) => {

    console.log(action.type);
    switch (action.type) {
        case 'GET_PRICE_FULFILLED':
            {
                return {
                    ...state,
                   priceData : action.payload.data
                }
            }

            case 'GET_SENTIMENTS_FULFILLED':
            {
                return {
                    ...state,
                   sentimentsData : action.payload.data
                }
            }
    
        default:
            {
                return state;
            }
    }
}

export default sentimentDetailsReducer;
