import { connect } from 'react-redux';

import { login } from '../actions'
import LoginPage from '../components/LoginPage';

const mapStateToProps = (state, ownProps) => {
  return {
    loginFailed: state.login.failed,
    loginRedirect: ownProps.location.state && ownProps.location.state.nextPathname
  }
}

const mapDispatchToProps = (dispatch) => {
  return {
    onLoginClick: (loginRedirect, username, password) => {
      dispatch(login(loginRedirect, username, password))
    }
  }
}

const LoginContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(LoginPage)

export default LoginContainer;
