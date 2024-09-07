// firebaseConfig.js
const { initializeApp } = require("firebase/app");
const { getAuth } = require("firebase/auth");

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyDZRT-ZOKfQ9ylKS2eiBD5fmjvteOq0Ls0",
  authDomain: "pioneer-43aee.firebaseapp.com",
  projectId: "pioneer-43aee",
  storageBucket: "pioneer-43aee.appspot.com",
  messagingSenderId: "543866876592",
  appId: "1:543866876592:web:8cea35dc7d63f5b57cc175",
  measurementId: "G-XFKSX30M03"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

module.exports = { auth };