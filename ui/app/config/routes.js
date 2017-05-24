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
import { checkSession } from '../utils';

const loggerMiddleware = createLogger()

const store = createStore(
  rootReducer,
  applyMiddleware(
    thunkMiddleware, // lets us dispatch() functions
    loggerMiddleware // neat middleware that logs actions
  )
);

function requireAuth(nextState, replace, next) {
  checkSession()
  .then((validSession) => {
    if (!validSession) {
      replace({
        pathname: '/login',
        state: { nextPathname: nextState.location.pathname }
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
        </Route>
      </Router>
    </MuiThemeProvider>
  </Provider>
);

module.exports = routes;
