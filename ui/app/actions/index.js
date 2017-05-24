import { api } from '../utils';
import * as types from './types';

const apiError = (res) => {
  return {
    type: types.API_ERROR,
    res
  }
}

const loading = () => {
  return {
    type: types.LOADING // Send what's loaded?
  }
}

const loginSuccess = () => {
  return {
    type: types.LOGIN_SUCCESS
  }
}

const loginFailed = () => {
  return {
    type: types.LOGIN_FAILED
  }
}

export const login = (username, password) => {
  return (dispatch) => {
    // TODO: dispatch(loading())
    return api.post('/session', {
      username: username,
      password: password
    })
    .then((res) => {
      if (res.status == 200) {
        localStorage.setItem('csrf_token', res.data.csrf_token);
        dispatch(loginSucess())

      } else if (res.status == 401 || res.status == 400)
        dispatch(loginFailed())
      else
        dispatch(apiError(res))
    });
  }
}
