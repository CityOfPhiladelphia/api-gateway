import { combineReducers } from 'redux';
import * as types from '../actions/types';

function login(state = {}, action) {
  return state;
}

function other(state = {}, action) {
  return state;
}

const rootReducer = combineReducers({
  login,
  other
});

export default rootReducer;
