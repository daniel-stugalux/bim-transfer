import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import App from './App';
import { MuiThemeProvider, createMuiTheme } from '@material-ui/core/styles';

const thema = createMuiTheme({
  palette: {
      secondary: {
          main: '#102538'
      }
    },
});

ReactDOM.render(
  (
    <MuiThemeProvider theme={thema}>
      <App />
    </MuiThemeProvider>
  ),
  document.getElementById('root')
);
