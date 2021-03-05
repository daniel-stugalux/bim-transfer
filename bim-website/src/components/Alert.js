import React from 'react';
import { makeStyles } from '@material-ui/core/styles';
import Snackbar from '@material-ui/core/Snackbar';
import MuiAlert from '@material-ui/lab/Alert';
import Typography from '@material-ui/core/Typography';
import SuccessImage from '../media/success.png';
import FailImage from '../media/fail.png';

const useStyles = makeStyles((theme) => ({
    image: {
        maxHeight: 200, 
        marginTop: '20px',
        position: 'relative',
        left: '50%',
        transform: 'translate(-50%, 0%)'
    }
}));



const Alert = (props) => {
    const classes = useStyles();

    const boom = props.severity === 'error' ?  
                                    <img src={FailImage} alt="Fail" className={classes.image}/> :
                                    <img src={SuccessImage} alt="Success" className={classes.image}/>;
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
            <MuiAlert severity={props.severity} onClose={props.handleClose} style={{display: 'flex'}}>
                <div>{message}</div>                
                <div>{boom}</div>
            </MuiAlert>
        </Snackbar>
    )
};

export default Alert;