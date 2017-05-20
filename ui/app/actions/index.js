import * as types from './types';

const api = axios.create({
  baseURL: 'http://localhost:8000'
});

api.interceptors.request.use((config) => {
  // TODO: add csrf header if method is unsafe
  return config;
});

api.interceptors.response.use((response) => {
  // TODO: log errors
  return response;
});

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

const loginSuccess = (data) => {
  return {
    type: types.LOGIN_SUCCESS,
    data
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
      if (res.status == 200)
        dispatch(loginSucess(res.data))
      else if (res.status == 401 || res.status == 400)
        dispatch(loginFailed())
      else
        dispatch(apiError(res))
    });
  }
}
