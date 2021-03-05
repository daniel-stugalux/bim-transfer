import React from 'react';
import Snackbar from '@material-ui/core/Snackbar';
import MuiAlert from '@material-ui/lab/Alert';
import Typography from '@material-ui/core/Typography';


const Alert = (props) => {
    // const boom = props.severity === 'success' ? <img src={SuccessImage} alt="Success" /> : <img src={FailImage} alt="Fail" />
    var message = undefined;
    try {
        message = props.message.map(e => <Typography>{e}</Typography>);
    } catch (error) {
        message = props.message;
    }
    return (
        <Snackbar
            anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
            open={props.open}
            onClose={props.handleClose}
            style={{marginTop: '50px'}}
        >
            <MuiAlert severity={props.severity} onClose={props.handleClose}>
                {
                    message
                }
            </MuiAlert>
        </Snackbar>
    )
};

export default Alert;