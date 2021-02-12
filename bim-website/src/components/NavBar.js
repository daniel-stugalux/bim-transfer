import React from 'react';
import AppBar from '@material-ui/core/AppBar';
import Toolbar from '@material-ui/core/Toolbar';
import Typography from '@material-ui/core/Typography';
import BIM360Logo from '../media/bim-360-docs-logo.png';
import StugaluxLogo from '../media/stugalux-logo-white.png';

class NavBar extends React.Component{
	render() {
		return (
			<div>
				<AppBar position="static">
					<Toolbar style={{backgroundColor: '#102538'}}>
                        <img src={BIM360Logo} alt="BIM 360 Docs" style={{width: '160px', marginRight: '12px'}}/>
						<Typography variant="subtitle1" color="inherit" style={{minWidth: '120px'}}>
							|  File publisher
						</Typography>
                        <img src={StugaluxLogo} alt="Stugalux" width='140px' style={{position: 'absolute', right: '30px'}}/>
					</Toolbar>
				</AppBar>
			</div>
		)
	}
}

export default NavBar;