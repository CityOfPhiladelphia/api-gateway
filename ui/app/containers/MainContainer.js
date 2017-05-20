import React from 'react';
import {List, ListItem} from 'material-ui/List';
import ActionAccountCircle from 'material-ui/svg-icons/action/account-circle';
import AppBar from 'material-ui/AppBar';
import Drawer from 'material-ui/Drawer';
import RightBar from 'material-ui/svg-icons/content/inbox';
import IconButton from 'material-ui/IconButton';
import IconMenu from 'material-ui/IconMenu';
import MenuItem from 'material-ui/MenuItem';
import FlatButton from 'material-ui/FlatButton';
import Toggle from 'material-ui/Toggle';
import MoreVertIcon from 'material-ui/svg-icons/navigation/more-vert';
import NavigationClose from 'material-ui/svg-icons/navigation/close';
import classnames from 'classnames';

import SideNavContainer from './SideNavContainer'

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
      open: true,
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
          className={classnames('app-bar', {'expanded': this.state.open})}
          onLeftIconButtonTouchTap={this.handleToggle.bind(this)}
          iconElementRight={<UserAppBar />} />
        <Drawer
          docked={true}
          open={this.state.open}
          zDepth={1}
          onRequestChange={(open) => this.setState({open})}>
          <img
            src='/img/logo/city-of-philadelphia.svg'
            alt='City of Philadelphia'
            style={{
              margin: '1em auto',
              maxWidth: '200px',
              display: 'block'}} />
          <h3 style={{textAlign: 'center'}}>API Gateway</h3>
          <SideNavContainer />
        </Drawer>
        <div className={classnames('app-content', {'expanded': this.state.open})}>
          { this.props.children }
        </div>
      </div>
    );
  }
}
