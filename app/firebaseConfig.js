import AsyncStorage from '@react-native-async-storage/async-storage';
import {getApp, getApps, initializeApp} from 'firebase/app';
import {getAuth, getReactNativePersistence, initializeAuth} from 'firebase/auth';
import {getFirestore} from 'firebase/firestore';

const firebaseConfig = {
  apiKey: process.env.EXPO_PUBLIC_FIREBASE_API_KEY || 'AIzaSyAmnbDT48iQW8SpxUZyTQh__HwM0yWgOwY',
  authDomain: process.env.EXPO_PUBLIC_FIREBASE_AUTH_DOMAIN || 'raioxeleicoes2026.firebaseapp.com',
  projectId: process.env.EXPO_PUBLIC_FIREBASE_PROJECT_ID || 'raioxeleicoes2026',
  storageBucket: process.env.EXPO_PUBLIC_FIREBASE_STORAGE_BUCKET || 'raioxeleicoes2026.firebasestorage.app',
  messagingSenderId: process.env.EXPO_PUBLIC_FIREBASE_MESSAGING_SENDER_ID || '982564347981',
  appId: process.env.EXPO_PUBLIC_FIREBASE_APP_ID || '1:982564347981:android:b4cdbb08002ed98226fc04',
};

export const firebaseReady = Boolean(firebaseConfig.apiKey && firebaseConfig.projectId && firebaseConfig.appId);

let app = null;
let auth = null;
let db = null;

if (firebaseReady) {
  app = getApps().length ? getApp() : initializeApp(firebaseConfig);
  try {
    auth = initializeAuth(app, {persistence: getReactNativePersistence(AsyncStorage)});
  } catch {
    auth = getAuth(app);
  }
  db = getFirestore(app);
}

export {app, auth, db};
