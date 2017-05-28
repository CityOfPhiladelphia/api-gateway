import React from 'react';
import ActionAccountCircle from 'material-ui/svg-icons/action/account-circle';
import AppBar from 'material-ui/AppBar';
import Drawer from 'material-ui/Drawer';
import Dashboard from 'material-ui/svg-icons/action/dashboard';
import VpnKey from 'material-ui/svg-icons/communication/vpn-key';
import Security from 'material-ui/svg-icons/hardware/security';
import IconButton from 'material-ui/IconButton';
import IconMenu from 'material-ui/IconMenu';
import MenuItem from 'material-ui/MenuItem';
import Divider from 'material-ui/Divider';

const UserAppBar = (props) => (
  <IconMenu
    {...props}
    iconButtonElement={
      <IconButton style={{ padding: 0, marginRight: 4 }} iconStyle={{ width: 48, height: 48 }}><ActionAccountCircle /></IconButton>
    }
    targetOrigin={{horizontal: 'right', vertical: 'top'}}
    anchorOrigin={{horizontal: 'right', vertical: 'top'}}
  >
    <MenuItem primaryText="Profile" />
    <MenuItem primaryText="Sign out" />
  </IconMenu>
);

UserAppBar.muiName = 'IconMenu';

export default class Main extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      open: false,
      logged: false
    };
  }

  handleToggle() {
    this.setState({ open: !this.state.open });
  }

  render() {
    return (
      <div>
        <AppBar
          onLeftIconButtonTouchTap={this.handleToggle.bind(this)}
          iconElementRight={<UserAppBar />} />
        <Drawer
          docked={false}
          open={this.state.open}
          onRequestChange={this.handleToggle.bind(this)}>
          <img
            src='/img/logo/city-of-philadelphia.svg'
            alt='City of Philadelphia'
            style={{
              margin: '1em auto',
              maxWidth: '200px',
              display: 'block'}} />
          <h3 style={{textAlign: 'center'}}>API Gateway</h3>
          <Divider />
          <MenuItem leftIcon={<Dashboard />} primaryText='Dashboard' />
          <MenuItem leftIcon={<VpnKey />} primaryText='API Keys' />
          <MenuItem leftIcon={<Security/>} primaryText='Bans' />
        </Drawer>
        { this.props.children }
      </div>
    );
  }
}
