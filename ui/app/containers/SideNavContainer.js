import React from 'react';
var PropTypes = React.PropTypes;
import {List, ListItem, makeSelectable} from 'material-ui/List';

let SelectableList = makeSelectable(List);

function wrapState(ComposedComponent) {
  class SelectableList extends React.Component {
    componentWillMount() {
      this.setState({
        selectedPath: this.props.defaultPath,
      });
    }

    handleRequestChange(event, index) {
      this.setState({
        selectedPath: index,
      });
      this.props.onSelectionChange(index);
    };

    render() {
      return (
        <ComposedComponent
          value={this.state.selectedPath}
          onChange={this.handleRequestChange.bind(this)}
        >
          {this.props.children}
        </ComposedComponent>
      );
    }
  };
  SelectableList.propTypes = {
    children: PropTypes.node.isRequired,
    defaultPath: PropTypes.string.isRequired,
    onSelectionChange: PropTypes.func.isRequired
  };
  return SelectableList;
}

SelectableList = wrapState(SelectableList);

class SideNav extends React.Component {
  constructor(props) {
    super(props);
  }

  handleSelectionChange(path) {
    this.context.router.push(path);
  }

  render() {
    return (
      <SelectableList
        defaultPath='/dashboard'
        onSelectionChange={this.handleSelectionChange.bind(this)}>
        <ListItem
          value='/dashboard'
          primaryText="Dashboard" />
        <ListItem
          value='/keys'
          primaryText="API Keys" />
        <ListItem
          value='/bans'
          primaryText="Bans" />
      </SelectableList>
    );
  }
}

SideNav.contextTypes = {
  router: React.PropTypes.object.isRequired
}

export default SideNav
