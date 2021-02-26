import React, { useState } from 'react';
import TextField from '@material-ui/core/TextField';
import { makeStyles } from '@material-ui/core/styles';
import NavBar from '../../components/NavBar.js';
import Alert from '../../components/Alert.js';
import Typography from '@material-ui/core/Typography';
import CircularProgress from '@material-ui/core/CircularProgress';
import { MuiThemeProvider, createMuiTheme } from '@material-ui/core/styles';
import Button from '@material-ui/core/Button';
import { Redirect } from 'react-router-dom';
import axios from 'axios';
import Cookies from'js-cookie';
import config from '../../config.json';

const thema = createMuiTheme({
    palette: {
        secondary: {
            main: '#102538'
        }
      },
});

const useStyles = makeStyles((theme) => ({
    root: {
        width: '800px',
        margin: 'auto'
    },
    margin: {
        margin: theme.spacing(1),
        position: 'absolute',
        top: '50%',
        left: '50%',
        transform: 'translate(-50%, -50%)'
    },
    urltextfield: {
        width: '600px',
        minWidth: '300px'
    }
}));

const CustomButtom = (props) => {
    const boom = props.loading ? <CircularProgress color="secondary" size={32}/> : "Transfer"
    return (
        <MuiThemeProvider theme={thema}>
            <Button
                variant="contained"
                color="secondary"
                style={{ marginLeft: 20, marginTop: 8, height: 40, width: 100 }}
                onClick={props.handler}
                disabled={props.disabled}>
                {boom}
            </Button>
        </MuiThemeProvider>
    )
}

const Transfer = () => {
    const classes = useStyles();
    const [url, setUrl] = useState('');
    const [loading, setLoading] = useState(false);
    const [buttonDisabled, setButtomDisabled] = useState(false);
    const [open, setOpen] = useState(false);
    const [alertMessage, setAlertMessage] = useState('');
    const [alertSeverity, setAlertSeverity] = useState('success');

    const handleAlertClose = (event, reason) => {
        if (reason !== 'clickaway') {
            setOpen(false);
        }
    }

    if (Cookies.get('access_token') === undefined){
        return <Redirect to="/" />;
    }

    const handleTranfer = () => {
        setLoading(true);
        setButtomDisabled(true);
        const data = {
            'access_token': Cookies.get('access_token'),
            'model_url': url
        }
        const transferApiUri = config.TRANSFER_URI;
        axios.post(transferApiUri, data)
            .then(function (response) {
                setLoading(false);
                setButtomDisabled(false);
                setAlertMessage("Success");
                setAlertSeverity('success');
                setOpen(true);
                setUrl('');
                // TODO : When success, show what files where uploaded and where
            }).catch(function (error) {
                setLoading(false);
                setButtomDisabled(false);   
                setOpen(true);
                setAlertMessage(error.response.data);
                setAlertSeverity('error');
                setUrl('');
            });
    }

    return (
        <div>
            <NavBar />
            <div className={classes.margin}>
                <Typography 
                    variant="h3" 
                    color="textPrimary" 
                    style={{ marginLeft: 60, marginBottom: 20, maxHeight: 50 }}>
                    Insert the model's URL
                </Typography>
                <div>
                    <TextField
                        label="Model URL"
                        variant="outlined"
                        id="model-input"
                        className={classes.urltextfield}
                        value={url} 
                        onChange={e => setUrl(e.target.value)}
                    />
                    <CustomButtom handler={handleTranfer} loading={loading} disabled={buttonDisabled} />
                </div>
            </div>
            <Alert 
                open={open} 
                handleClose={handleAlertClose} 
                severity={alertSeverity} 
                message={alertMessage}/>
        </div>
    );
}

export default Transfer;
