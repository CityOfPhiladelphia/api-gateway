import React from 'react';
const PropTypes = React.PropTypes;
import Paper from 'material-ui/Paper';
import TextField from 'material-ui/TextField';
import RaisedButton from 'material-ui/RaisedButton';

const styles = {
  loginPaper: {
    height: 250,
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

  render() {
    return (
      <Paper style={styles.loginPaper} zDepth={1}>
        <TextField
          style={styles.loginTextFields}
          onChange={this.updateUsername.bind(this)}
          floatingLabelText='Username' />
        <TextField
          style={styles.loginTextFields}
          onChange={this.updatePassword.bind(this)}
          floatingLabelText='Password'
          type='password' />
        <RaisedButton
          style={styles.loginButton}
          onTouchTap={this.props.onLogin.bind(this)}
          label="Login"
          primary={true} />
      </Paper>
    );
  }
}

Login.propTypes = {
  onLogin: PropTypes.func
};

export default Login;
