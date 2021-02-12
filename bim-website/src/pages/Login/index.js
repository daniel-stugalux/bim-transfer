import React, { useCallback } from 'react';
import NavBar from '../../components/NavBar';
import Button from '@material-ui/core/Button';
import { Redirect } from 'react-router-dom';
import config from '../../config.json';
import Cookies from 'js-cookie';
import './style.css';

const Login = () => {
    const handleLogin = useCallback(async () => {

        const qParams = [
            `redirect_uri=${config.CALLBACK_URL}`,
            `client_id=${config.CLIENT_ID}`,
            `scope=${config.SCOPES}`,
            `response_type=${config.RESPONSE_TYPE}`
        ].join("&");

        try {
            window.location.assign(`${config.OAUTH_URL}?${qParams}`);
        } catch (e) {
            console.error(e);
        }

    }, []);
    
    if (Cookies.get('access_token') !== undefined){
        return <Redirect to="/dashboard" />;
    }

    return (
        <>
            <NavBar />
            <div style={{ textAlign: 'center', minHeight: '300px' }}>
                <Button variant="outlined" id="autodeskSigninButton" color='primary' onClick={handleLogin}>
                    <img src="https://github.com/Autodesk-Forge/bim360appstore-data.management-nodejs-transfer.storage/raw/master/www/img/autodesk_text.png"
                        height="20" alt="tao" /> Sign in
                </Button>
            </div>
        </>
    );
}

export default Login;