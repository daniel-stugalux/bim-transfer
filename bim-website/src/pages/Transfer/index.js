import React, { useState } from 'react';
import TextField from '@material-ui/core/TextField';
import { makeStyles } from '@material-ui/core/styles';
import NavBar from '../../components/NavBar.js';
import Typography from '@material-ui/core/Typography';
import Button from '@material-ui/core/Button';
import { Redirect } from 'react-router-dom';
import axios from 'axios';
import Cookies from'js-cookie';
import config from '../../config.json';


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

const Transfer = () => {
    const classes = useStyles();
    const [url, setUrl] = useState('');

    if (Cookies.get('access_token') === undefined){
        return <Redirect to="/" />;
    }

    const handleTranfer = () => {
        console.log('\n\n\nTAOOO\n\n\n');
        const data = {
            'access_token': Cookies.get('access_token'),
            'model_url': url
        }
        const transferApiUri = config.TRANSFER_URI;
        console.log(transferApiUri);
        axios.post(transferApiUri, data)
            .then(function (response) {
                console.log(response.data);
            }).catch(function (error) {
                if (error.response) {
                  console.log(error.response.headers);
                } 
                else if (error.request) {
                  console.log(error.request);
                } 
                else {
                  console.log(error);
                  console.log(error.message);
                }
                console.log(error.config);
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
                    <Button
                        variant="contained"
                        color="primary"
                        style={{ marginLeft: 20, marginTop: 10, maxHeight: 50 }}
                        onClick={handleTranfer}>
                        Transfer
                    </Button>
                </div>
            </div>
        </div>
    );
}

export default Transfer;
