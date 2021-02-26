import React from 'react';
import { Redirect } from 'react-router-dom';
import Cookies from 'js-cookie';

const OAuthCallback = ({ location }) => {
    const token = (location.hash.match(/access_token=([^&]+)/) || [])[1];

    if (token !== undefined) {
        Cookies.set('access_token', token, { expires: 1 })
        return <Redirect to="/dashboard" />;
    } else {
        return <Redirect to="/" />;
    }
}

export default OAuthCallback;