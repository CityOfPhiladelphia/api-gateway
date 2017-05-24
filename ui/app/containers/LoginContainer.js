import { connect } from 'react-redux';

import { login } from '../actions'
import LoginPage from '../components/LoginPage';

const mapStateToProps = (state, ownProps) => {
  console.log(state)
  console.log(ownProps)
  return {
    loginFailed: state.login.failed,
    loginRedirect: ownProps.location.state.nextPathname
  }
}

const mapDispatchToProps = (dispatch) => {
  console.log(this)
  console.log(arguments)
  return {
    onLoginClick: (username, password) => {
      console.log(this)
      dispatch(login(username, password))
    }
  }
}

const LoginContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(LoginPage)

export default LoginContainer;
