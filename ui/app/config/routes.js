import React from 'react';
import { Router, Route, IndexRoute, hashHistory } from 'react-router';
import { Provider } from 'react-redux';
import thunkMiddleware from 'redux-thunk';
import { createLogger } from 'redux-logger';
import { createStore, applyMiddleware } from 'redux';
import MuiThemeProvider from 'material-ui/styles/MuiThemeProvider';
import getMuiTheme from 'material-ui/styles/getMuiTheme';

import theme from '../styles/theme';
import ListKeysContainer from '../containers/ListKeysContainer';
import LoginContainer from '../containers/LoginContainer';
import MainContainer from '../containers/MainContainer';
import rootReducer from '../reducers';
import { checkSession } from '../utils';
import * as types from '../actions/types';

const loggerMiddleware = createLogger()

const redirectMiddleware = store => next => action => {
  if (action.type == types.REDIRECT)
    return hashHistory.replace(action.redirect || { pathname: '/' });
  next(action);
}

const store = createStore(
  rootReducer,
  applyMiddleware(
    thunkMiddleware, // lets us dispatch() functions
    loggerMiddleware, // neat middleware that logs actions
    redirectMiddleware
  )
);

function requireAuth(nextState, replace, next) {
  checkSession()
  .then((validSession) => {
    if (!validSession) {
      replace({
        pathname: '/login',
        state: { nextPathname: nextState.location }
      });
      next();
    } else
      next();
  });
}

var routes = (
  <Provider store={store}>
    <MuiThemeProvider muiTheme={getMuiTheme(theme)}>
      <Router history={hashHistory}>
        <Route path='/login' component={LoginContainer} />
        <Route path='/' component={MainContainer} onEnter={requireAuth}>
          <Route path='/dashboard' />
          <Route path='/keys' component={ListKeysContainer} />
        </Route>
      </Router>
    </MuiThemeProvider>
  </Provider>
);

module.exports = routes;
