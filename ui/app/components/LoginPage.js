import React from 'react';
import PropTypes from 'prop-types';

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

class LoginPage extends React.Component {
  constructor(props) {
    super(props);
  }

  render() {
    return (
      <div>
        <img
          src='/img/logo/city-of-philadelphia.svg'
          alt='City of Philadelphia'
          style={styles.logo} />
        <h3 style={styles.title}>API Gateway</h3>
        <Login
          onLoginClick={this.props.onLoginClick}
          loginFailed={this.props.loginFailed} />
      </div>
    );
  }
}

LoginPage.propTypes = {
  onLoginClick: PropTypes.func,
  loginFailed: PropTypes.bool,
  loginRedirect: PropTypes.string
};

export default LoginPage;
