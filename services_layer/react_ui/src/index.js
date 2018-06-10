import React from 'react';
import ReactDOM from 'react-dom';
import { Provider } from 'react-redux';
import { applyMiddleware, createStore } from 'redux';
import promiseMiddleware from 'redux-promise-middleware';
import App from './components/app';
import reducers from './reducers/index.js';

const middleware = [promiseMiddleware()];

const configureStore = (initialState) => {
    const store = createStore(reducers, initialState, applyMiddleware(...middleware));;

    return store ;
}

ReactDOM.render(
  <Provider store={configureStore({})}>
    <App />
  </Provider>
  , document.querySelector('.container'));
