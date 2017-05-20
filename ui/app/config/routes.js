import React from 'react';
import { Router, Route, IndexRoute, hashHistory } from 'react-router';
import { Provider } from 'react-redux';
import thunkMiddleware from 'redux-thunk';
import { createLogger } from 'redux-logger';
import { createStore, applyMiddleware } from 'redux';
import MuiThemeProvider from 'material-ui/styles/MuiThemeProvider';
import getMuiTheme from 'material-ui/styles/getMuiTheme';

import theme from '../styles/theme';
import LoginContainer from '../containers/LoginContainer';
import MainContainer from '../containers/MainContainer';
import rootReducer from '../reducers';

const loggerMiddleware = createLogger()

const store = createStore(
  rootReducer,
  applyMiddleware(
    thunkMiddleware, // lets us dispatch() functions
    loggerMiddleware // neat middleware that logs actions
  )
);

function requireAuth(nextState, replace) { // https://medium.com/@onclouds/react-js-react-router-redirect-after-login-412c83122c98
  // TODO: GET /session to check?
  // TODO: check for csrf_token in localStorage or sessionStorage ?
  if (!SignInStorage.isSignedin()) {
    replace({
      pathname: '/signin',
      state: { nextPathname: nextState.location.pathname }
    });
  }
}

var routes = (
  <Provider store={store}>
    <MuiThemeProvider muiTheme={getMuiTheme(theme)}>
      <Router history={hashHistory}>
        <Route path='/login' component={LoginContainer} />
        <Route path='/' component={MainContainer}> // onEnter={requireAuth}
        </Route>
      </Router>
    </MuiThemeProvider>
  </Provider>
);

module.exports = routes;
