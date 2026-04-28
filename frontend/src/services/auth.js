import { initializeApp } from "firebase/app";
import { 
  getAuth, 
  signInWithPopup, 
  GoogleAuthProvider,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  sendEmailVerification,
  signOut,
  onAuthStateChanged
} from "firebase/auth";

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID
};

// Gracefully handle missing/invalid Firebase config
let app = null;
let auth = null;
let googleProvider = null;
let firebaseReady = false;

try {
  if (firebaseConfig.apiKey && firebaseConfig.apiKey !== 'undefined') {
    app = initializeApp(firebaseConfig);
    auth = getAuth(app);
    googleProvider = new GoogleAuthProvider();
    googleProvider.addScope('https://www.googleapis.com/auth/drive.file');
    firebaseReady = true;
  } else {
    console.warn('Firebase config not found. Auth features disabled.');
  }
} catch (err) {
  console.warn('Firebase initialization failed:', err.message);
}

export { auth, firebaseReady };

export const loginWithGoogle = async () => {
  if (!firebaseReady) throw new Error('Firebase is not configured. Please add your API keys.');
  try {
    const result = await signInWithPopup(auth, googleProvider);
    const credential = GoogleAuthProvider.credentialFromResult(result);
    const token = credential.accessToken;
    const user = result.user;
    
    if (token) {
      localStorage.setItem('googleOAuthToken', token);
    }
    
    return { user, token };
  } catch (error) {
    throw error;
  }
};

export const loginWithEmail = async (email, password) => {
  if (!firebaseReady) throw new Error('Firebase is not configured.');
  try {
    const result = await signInWithEmailAndPassword(auth, email, password);
    if (!result.user.emailVerified) {
      throw new Error("Please verify your email address before logging in.");
    }
    return result.user;
  } catch (error) {
    throw error;
  }
};

export const registerWithEmail = async (email, password) => {
  if (!firebaseReady) throw new Error('Firebase is not configured.');
  try {
    const result = await createUserWithEmailAndPassword(auth, email, password);
    await sendEmailVerification(result.user);
    await signOut(auth);
    return result.user;
  } catch (error) {
    throw error;
  }
};

export const logout = async () => {
  localStorage.removeItem('googleOAuthToken');
  if (auth) return signOut(auth);
};

export const subscribeToAuthChanges = (callback) => {
  if (!auth) {
    // No Firebase — immediately call back with null user so app still renders
    callback(null);
    return () => {};
  }
  return onAuthStateChanged(auth, callback);
};
