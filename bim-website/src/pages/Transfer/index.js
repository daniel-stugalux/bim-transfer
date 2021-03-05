import React, { useState } from 'react';
import TextField from '@material-ui/core/TextField';
import { makeStyles } from '@material-ui/core/styles';
import NavBar from '../../components/NavBar.js';
import Alert from '../../components/Alert.js';
import Typography from '@material-ui/core/Typography';
import CircularProgress from '@material-ui/core/CircularProgress';
import Button from '@material-ui/core/Button';
import IconButton from '@material-ui/core/IconButton';
import InfoOutlinedIcon from '@material-ui/icons/InfoOutlined';
import { Redirect } from 'react-router-dom';
import axios from 'axios';
import Cookies from'js-cookie';
import config from '../../config.json';
import GifDialog from '../../components/GifDialog.js';


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
        <Button
            variant="contained"
            color="secondary"
            style={{ marginLeft: 20, marginTop: 8, height: 40, width: 100 }}
            onClick={props.handler}
            disabled={props.disabled}>
            {boom}
        </Button>
    )
}

const Transfer = () => {
    const classes = useStyles();
    const [url, setUrl] = useState('');
    const [loading, setLoading] = useState(false);
    const [buttonDisabled, setButtomDisabled] = useState(false);
    const [open, setOpen] = useState(false);
    const [dialogOpen, setDialogOpen] = useState(false);
    const [alertMessage, setAlertMessage] = useState('');
    const [alertSeverity, setAlertSeverity] = useState('success');

    const handleAlertClose = (event, reason) => {
        if (reason !== 'clickaway') {
            setOpen(false);
        }
    }

    const handleDialogClose = () => {
        setDialogOpen(false);
    }

    if (Cookies.get('access_token') === undefined){
        return <Redirect to="/" />;
    }

    const handleTranfer = () => {
        setLoading(true);
        setButtomDisabled(true);
        setOpen(false);
        const data = {
            'access_token': Cookies.get('access_token'),
            'model_url': url
        }
        const transferApiUri = config.TRANSFER_URI;
        axios.post(transferApiUri, data)
            .then(function (response) {
                setLoading(false);
                setButtomDisabled(false);
                setAlertMessage(response.data);
                setAlertSeverity(response.status === 200 ? 'success' : 'warning');
                setOpen(true);
                setUrl('');
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
                <div style={{display: 'flex'}}>
                    <Typography 
                        variant="h3" 
                        color="textPrimary" 
                        style={{ marginLeft: 60, marginBottom: 20, height: 50, width: 500 }}>
                        Insert the model's URL
                    </Typography>
                    <IconButton aria-label="info" color="secondary" style={{marginBottom: 25}}  onClick={() => setDialogOpen(true)}>
                        <InfoOutlinedIcon />
                    </IconButton>
                </div>
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
            <GifDialog onClose={handleDialogClose} open={dialogOpen}/>
        </div>
    );
}

export default Transfer;
