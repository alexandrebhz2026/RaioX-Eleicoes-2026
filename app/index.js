import React from 'react';
import {registerRootComponent} from 'expo';
import App from './App';
import AuthGate from './AuthGate';

function Root(){
  return <AuthGate><App /></AuthGate>;
}

registerRootComponent(Root);
