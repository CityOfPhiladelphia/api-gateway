import { combineReducers } from 'redux';
import * as types from '../actions/types';

function login(state = { failed: false, success: false }, action) {
  console.log(action.type)
  switch (action.type) {
    case types.LOGIN_FAILED:
      return Object.assign({}, state, {
        failed: true,
        success: false,
        redirected: false
      });
    case types.LOGIN_SUCCESS:
      return Object.assign({}, state, {
        failed: false,
        success: true,
        redirected: false
      });
    case types.LOGIN_REDIRECT:
      return Object.assign({}, state, {
        redirected: true
      });
    default:
      return state;
  }
}

function other(state = {}, action) {
  return state;
}

const rootReducer = combineReducers({
  login,
  other
});

export default rootReducer;
