import React from 'react';
import ReactDOM from 'react-dom';
import injectTapEventPlugin from 'react-tap-event-plugin';

injectTapEventPlugin();

import routes from './config/routes';

ReactDOM.render(
  routes,
  document.getElementById('app')
);
