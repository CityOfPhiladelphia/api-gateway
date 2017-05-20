import React from 'react';

import Login from '../components/Login';

const styles = {
  logo: {
    margin: '1em auto',
    maxWidth: '200px',
    display: 'block'
  },
  title: {
    textAlign: 'center',
    fontFamily: 'roboto'
  }
};

class LoginContainer extends React.Component {
  constructor(props) {
    super(props);
  }

  handleLogin() {
    // TODO: POST /session
    // TODO: save csrf_token to localStorage or sessionStorage
    // TODO: redirect to nextPathname
    console.log(this)
  }

  render() {
    return (
      <div>
        <img
          src='/img/logo/city-of-philadelphia.svg'
          alt='City of Philadelphia'
          style={styles.logo} />
        <h3 style={styles.title}>API Gateway</h3>
        <Login onLogin={this.handleLogin} />
      </div>
    );
  }
}

export default LoginContainer
