import React from 'react';
import Snackbar from '@material-ui/core/Snackbar';
import MuiAlert from '@material-ui/lab/Alert';
import SuccessImage from '../media/success.png';
import FailImage from '../media/fail.png';


const Alert = (props) => {
    const boom = props.severity === 'success' ? <img src={SuccessImage} alt="Success" /> : <img src={FailImage} alt="Fail" />
    return (
        <Snackbar
            anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
            open={props.open}
            onClose={props.handleClose}
            style={{marginTop: '50px'}}
        >
            <MuiAlert severity={props.severity} onClose={props.handleClose}>{boom}</MuiAlert>
        </Snackbar>
    )
};

export default Alert;