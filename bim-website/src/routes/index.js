import React from 'react';
import { Switch, Route } from 'react-router-dom';
import Login from '../pages/Login';
import Transfer from '../pages/Transfer';
import OAuthCallback from '../pages/OAuthCallback';


export default function Routes() {
    return (
        <Switch>
            <Route path="/api/forge/callback/oauth" component={OAuthCallback} />
            <Route path="/dashboard" component={Transfer} />
            <Route path="/" component={Login} />
            
            {/* redirect user to SignIn page if route does not exist and user is not authenticated */}
            <Route component={Login} />
        </Switch>
    );
}