import { createStore, applyMiddleware } from 'redux';
import createSagaMiddleware from 'redux-saga';
import logger from 'redux-logger';
import { composeWithDevTools } from 'redux-devtools-extension';

import reducer from './reducers';
import rootSaga from './sagas';

const sagaMiddleware = createSagaMiddleware();
const env = process.env.NODE_ENV;
const middlewares = env === 'development'
  ? composeWithDevTools(applyMiddleware(sagaMiddleware, logger))
  : applyMiddleware(sagaMiddleware);

const store = createStore(reducer, middlewares);
sagaMiddleware.run(rootSaga);

export default store;
