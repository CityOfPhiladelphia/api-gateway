import React from 'react';
import PropTypes from 'prop-types';
import Paper from 'material-ui/Paper';
import TextField from 'material-ui/TextField';
import RaisedButton from 'material-ui/RaisedButton';

const styles = {
  loginPaper: {
    width: 300,
    margin: '0 auto 0 auto',
    textAlign: 'center',
    display: 'block'
  },
  loginTextFields: {
    marginTop: 10,
    display: 'inline-block'
  },
  loginButton: {
    margin: 20,
    display: 'inline-block'
  }
};

class Login extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      username: '',
      password: ''
    }
  }

  updateUsername(e, value) {
    this.setState({
      username: value.trim()
    });
  }

  updatePassword(e, value) {
    this.setState({
      password: value.trim()
    });
  }

  handleLogin(e) {
    e.preventDefault();
    this.props.onLoginClick(this.state.username, this.state.password);
  }

  render() {
    return (
      <Paper style={styles.loginPaper} zDepth={1}>
        <form onSubmit={this.handleLogin.bind(this)}>
          <TextField
            style={styles.loginTextFields}
            onChange={this.updateUsername.bind(this)}
            errorText={this.props.loginFailed ? 'Username or password does not match' : ''}
            floatingLabelText='Username' />
          <TextField
            style={styles.loginTextFields}
            onChange={this.updatePassword.bind(this)}
            errorText={this.props.loginFailed ? 'Username or password does not match' : ''}
            floatingLabelText='Password'
            type='password' />
          <RaisedButton
            style={styles.loginButton}
            type="submit"
            label="Login"
            primary={true} />
        </form>
      </Paper>
    );
  }
}

Login.propTypes = {
  onLoginClick: PropTypes.func,
  loginFailed: PropTypes.bool
};

export default Login;
