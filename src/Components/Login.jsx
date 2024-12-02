import React, { useState } from 'react';
import TextField from '@mui/material/TextField';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';
import axios from 'axios';
import bgImg from "../Assets/bg1.webp"; // Make sure the path to the image is correct
import { LoadingOutlined } from '@ant-design/icons';
import { Flex, Spin } from 'antd';
import { useNavigate } from 'react-router-dom';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import validator from 'validator';


export default function LogInForm() {
  const [loginData, setLogInData] = useState({
    email: '',
    password: ''
  });

  const navigate = useNavigate();
  const [loadingState, setLoadingState] = useState(false);
  const [emptyField, setEmptyFieldAlert] = useState(false);
  const [incorrectField, setIncorrectFieldAlert] = useState(false);
  const [alertMessage, setAlertMessage] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const spinnerStyle = {
    color: 'white', // Spinner color
    fontSize: 48,   // Adjust the spinner size
  };

  const handleSignUpChange = (e) => {
    const { name, value } = e.target;
    setLogInData((prevState) => ({
      ...prevState,
      [name]: value // Store value as-is
    }));

    // Reset alerts
    if (emptyField) {
      setEmptyFieldAlert(false);
    }
    if (incorrectField) {
      setIncorrectFieldAlert(false);
    }
    if (alertMessage) {
      setAlertMessage('');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log(loginData)
    if (loginData.email.trim() === '' || loginData.password.trim() === '') {
      // setEmptyFieldAlert(true);
      // setAlertMessage("Please Fill all the details");
      toast.error("Please fill all the details", {
        position: "top-center",
        style: {
          backgroundColor: '#f44336', // Red background for errors
          color: 'white' // White text
        },
      });
      return;
    }
    if (!validator.isEmail(loginData.email)) {
      // setIncorrectFieldAlert(true);
      // setAlertMessage("Please check the credentials");
      toast.warning("Please check the credentials", {
        position: "top-center",
        style: {
          backgroundColor: '#ff9800', // Orange background for warnings
          color: 'black' // Black text
        },
      });
      return;
    }
    if (loginData.password.trim().length < 6) {
      // setEmptyFieldAlert(true);
      // setAlertMessage("The password length should be greater than 5");
      toast.info("The password length should be greater than 5", {
        position: "top-center",
        style: {
          backgroundColor: '#2196f3', // Blue background for informational messages
          color: 'white' // White text
        },
      });
      return;
    }

    try {
      // Create a copy of signUpData excluding ConfirmPassword
      setSubmitted(true);
      setLoadingState(true);
      const response = await axios.post("http://localhost:5000/login", loginData);
      console.log(response);
      if (response.status === 200) {
        let userData = response.data.user;

        if (typeof userData === 'object' && userData !== null) {
          // Store the new object in localStorage
          localStorage.setItem('userDetails', JSON.stringify(userData));

          // console.log('New User Data:', newUserData);  // For debugging
          toast.success("Login successful!", {
            position: "top-center",
            style: {
              backgroundColor: '#4caf50', // Green background for success
              color: 'white' // White text
            },
          });
        } else {
          console.error('userData is not an object. Cannot create newUserData.');
        }
        setTimeout(() => {
          navigate('/');
          setLoadingState(false);
        }, 1000); // Delay of 3000ms (3 seconds)

      }
    }
    catch (error) {
      console.log(error);
      // setIncorrectFieldAlert(true);
      // setAlertMessage("Error at Registering User");
      toast.error("Error signing in", {
        position: "top-center",
        style: {
          backgroundColor: '#f44336', // Red background for errors
          color: 'white' // White text
        },
      });
    }
  };

  return (
    <>
      <ToastContainer
        position="top-center"
        autoClose={3000}
        hideProgressBar={false}
        newestOnTop={false}
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
        style={{ zIndex: 9999 }} // Ensures that the toasts appear on top of other elements
      />
      <Grid
        container
        justifyContent="center" // Center items horizontally
        alignItems="center" // Center items vertically
        style={{
          minHeight: '100vh',
          backgroundImage: `url(${bgImg})`, // Correct syntax for backgroundImage
          backgroundSize: 'cover', // Ensures the background covers the whole viewport
          backgroundPosition: 'center', // Centers the background image
          backgroundRepeat: 'no-repeat' // Prevents image repetition
        }}
      >
        <Grid item>
          <Box
            component="form"
            onSubmit={handleSubmit} // Handle form submission
            sx={{
              width: 350,
              display: 'flex',
              flexDirection: 'column',
              gap: 2,
              padding: 3,
              boxShadow: 3,
              borderRadius: 2,
              backgroundColor: 'rgba(209,236,252,255)', // Semi-transparent background for the form
              border: '2px solid #567350', // Green border
            }}
          >
            <Typography variant="h5" component="h1" align="center" sx={{ mb: 2, color: '#e6f4e4' }}>
              User LogIn Form
            </Typography>

            <TextField
              name='email'
              type='email'
              label='Email Address'
              variant='outlined'
              value={loginData.email}
              onChange={handleSignUpChange}
              error={emptyField}
              helperText={emptyField && "This field cannot be empty"}
              sx={{
                input: { color: 'rgba(58,62,64,255)' },
                fieldset: { borderColor: 'rgba(58,62,64,255)' },
                '& .MuiInputLabel-root': { color: 'rgba(58,62,64,255)' }, // Label color
                '& .MuiInputLabel-root.Mui-focused': { color: 'rgba(58,62,64,255)' }, // Label focus color
                '& input::placeholder': { color: 'white' } // Placeholder color
              }}
              InputLabelProps={{
                style: { color: 'white' } // Label color
              }}
              InputProps={{
                style: { color: 'white' }, // Input text color
                inputProps: {
                  style: { color: 'white' } // Placeholder color
                }
              }}
            />

            <TextField
              name='password'
              type='password'
              label='Password'
              variant='outlined'
              value={loginData.password}
              onChange={handleSignUpChange}
              error={emptyField}
              helperText={emptyField && "This field cannot be empty"}
              sx={{
                input: { color: '#e6f4e4' },
                fieldset: { borderColor: '#567350' },
                '& .MuiInputLabel-root': { color: '#e6f4e4' }, // Label color
                '& .MuiInputLabel-root.Mui-focused': { color: '#e6f4e4' }, // Label focus color
                '& input::placeholder': { color: 'white' } // Placeholder color
              }}
              InputLabelProps={{
                style: { color: 'white' } // Label color
              }}
              InputProps={{
                style: { color: 'white' }, // Input text color
                inputProps: {
                  style: { color: 'white' } // Placeholder color
                }
              }}
            />
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
              <Flex align="center" gap="middle">
                <Spin
                  spinning={loadingState}
                  indicator={<LoadingOutlined style={spinnerStyle} spin />}
                  size="large"
                />
              </Flex>
            </div>

            <Button
              variant="contained"
              type="submit"
              sx={{
                backgroundColor: '#567350', // Button background color
                color: '#e6f4e4', // Button text color
                '&:hover': {
                  backgroundColor: '#4a6d44' // Darker green on hover
                }
              }}
            >
              Submit
            </Button>
            {submitted && (
              <div className='result'>
                <div>
                  <h2 style={{ color: 'white' }}>Welcome {loginData.name}</h2>

                  <p style={{ color: 'white' }}>Created User with Credentials</p>
                  {/* <p style={{ color: 'white' }}>Name: {loginData.name}</p> */}
                  <p style={{ color: 'white' }}>Email: {loginData.email}</p>
                </div>
              </div>
            )}
          </Box>
        </Grid>

      </Grid>
    </>
  );
}