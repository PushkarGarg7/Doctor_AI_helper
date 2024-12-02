import React, { useState } from 'react';
import TextField from '@mui/material/TextField';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';
import axios from 'axios';
import bgImg from "../Assets/bg1.webp"; // Make sure the path to the image is correct
import { LoadingOutlined } from '@ant-design/icons';
import { Flex, Spin} from 'antd';
import {useNavigate } from 'react-router-dom';
import { ToastContainer, toast } from 'react-toastify';
import validator from 'validator';
export default function SignUpForm() {
  const [signUpData, setSignUpData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const navigate = useNavigate();
  const [emptyField, setEmptyFieldAlert] = useState(false);
  const [incorrectField, setIncorrectFieldAlert] = useState(false);
  const [alertMessage, setAlertMessage] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const [loadingState, setLoadingState] = useState(false);
  const handleSignUpChange = (e) => {
    const { name, value } = e.target;
    setSignUpData((prevState) => ({
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

  const spinnerStyle = {
    color: 'white', // Spinner color
    fontSize: 48,   // Adjust the spinner size
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (signUpData.name.trim() === '' || signUpData.email.trim() === '' || signUpData.password.trim() === '' || signUpData.confirmPassword.trim() === '') {
        // setEmptyFieldAlert(true);
        // setAlertMessage("Please Fill all the details");
        toast.error("Please fill all the details", { position: "top-center" });
        return;
    }
    if(!validator.isEmail(signUpData.email)){
        // setIncorrectFieldAlert(true);
        // setAlertMessage("Please check the credentials");
        toast.warning("Please check the credentials", { position: "top-center" });
        return;
    }
    if(signUpData.password.trim().length < 6){
        // setEmptyFieldAlert(true);
        // setAlertMessage("The password length should be greater than 5");
        toast.info("The password length should be greater than 5", { position: "top-center" });
        return;
    }
    if(signUpData.password !== signUpData.confirmPassword){
        // setIncorrectFieldAlert(true);
        // setAlertMessage("Confirm Password and Password both are not same");
        toast.error("Confirm Password and Password both are not the same", { position: "top-center" });
        return;
    }
    
    try {
        // Create a copy of signUpData excluding ConfirmPassword
        setLoadingState(true);
        const {confirmPassword, ...dataToSend} = signUpData;
        setSubmitted(true);
        const response = await axios.post("http://localhost:5000/register", dataToSend);
        
        if(response.status === 201){
          toast.success("Registration Successful! Redirecting to Login...", { position: "top-center" });
            setTimeout(() => {
                navigate('/login');
            }, 3000); // Delay of 3000ms (3 seconds)
            setLoadingState(false);
        }
    } 
    catch (error) {
        console.log(error);
        // setIncorrectFieldAlert(true);
        // setAlertMessage("Error at Registering User");
        toast.error("Error at Registering User", { position: "top-center" });
    }
  };

  return (
    <>
    <ToastContainer />

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
            backgroundColor: 'rgba(18, 18, 18, 0.8)', // Semi-transparent background for the form
            border: '2px solid #567350', // Green border
          }}
        >
          <Typography variant="h5" component="h1" align="center" sx={{ mb: 2, color: '#e6f4e4' }}>
            User Signup Form
          </Typography>

          <TextField
            name='name'
            label='Name'
            variant='outlined'
            value={signUpData.name}
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

          <TextField
            name='email'
            type='email'
            label='Email Address'
            variant='outlined'
            value={signUpData.email}
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

          <TextField
            name='password'
            type='password'
            label='Password'
            variant='outlined'
            value={signUpData.password}
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

          <TextField
            name='confirmPassword'
            type='password'
            label='Confirm Password'
            variant='outlined'
            value={signUpData.confirmPassword}
            onChange={handleSignUpChange}
            error={emptyField || incorrectField}
            helperText={(emptyField && "This field cannot be empty") || (incorrectField && "Passwords do not match")}
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
                   
          <Flex align="center" gap="middle">
            <Spin
              spinning={loadingState}
              indicator={<LoadingOutlined style={spinnerStyle} spin />}
              size="large"
            />
          </Flex>

          {submitted && (
          <div
            style={{
              backgroundColor: '#333',   // Dark background for contrast
              padding: '20px',           // Padding for spacing
              borderRadius: '10px',      // Rounded corners for a modern look
              textAlign: 'center',       // Center align text
            }}
          >
            <div>
              <h2 style={{ color: 'white', marginBottom: '10px' }}>Welcome {signUpData.name}</h2>

              <p style={{ color: 'white', marginBottom: '5px' }}>Created User with Credentials</p>
              <p style={{ color: 'white', marginBottom: '5px' }}>Name: {signUpData.name}</p>
              <p style={{ color: 'white', marginBottom: '20px' }}>Email: {signUpData.email}</p>

              <h2 style={{ color: 'white', marginTop: '20px' }}>Now Please Log In Again</h2>
            </div>
          </div>
        )}
        </Box>
      </Grid>

    </Grid>
    </>
  );
}
