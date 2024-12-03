import React from 'react';
import { TypeAnimation } from 'react-type-animation';
import '../Styles/LandingPage.css'; // Import the CSS for styling
import Navbar from './NavBar';
import { Card, CardContent, Typography, IconButton, Grid } from '@mui/material'; // Import necessary components
import LinkedInIcon from '@mui/icons-material/LinkedIn'; // LinkedIn icon
import GitHubIcon from '@mui/icons-material/GitHub'; // GitHub icon
import UploadFileIcon from '@mui/icons-material/UploadFile'; // or AttachFile
import BoltIcon from '@mui/icons-material/Bolt'; // For the Instant Insights feature
import VisibilityIcon from '@mui/icons-material/Visibility'; // or Search
import HeadsetIcon from '@mui/icons-material/Headset'; // or Audiotrack
// import RoundedButton from './RoundedButton'; // Import your RoundedButton component
import RoundedButton from './RoundedButton';
import Gaurav from '../Assets/Gaurav.jpeg';
import Abhinav from '../Assets/Abhinav.jpeg';
import Pushkar from '../Assets/Pushkar.jpeg';
import Chirag from '../Assets/Chirag.png';
import Shaunak from '../Assets/shaunak.jpg';
import Kanu from '../Assets/kanu.jpg';

const LandingPage = () => {
  const teamMembers = [
    {
      name: 'Shaunak Gupta',
      role: 'Backend Developer',
      linkedIn: '#',
      github: '#',
      image: Shaunak,
      description: 'Passionate about building innovative web applications, continuously learning new technologies, and striving to improve user experiences through creative solutions'
    },
    {
      name: 'Gaurav Goyal',
      role: 'Dev-Ops Engineer',
      linkedIn: '#',
      github: '#',
      image: Gaurav,
      description: 'A specialist in automating, managing, and optimizing software development and deployment processes to ensure seamless integration and delivery'
    },
    {
      name: 'Abhinav Aggarwal',
      role: 'Frontend Engineer',
      linkedIn: '#',
      github: '#',
      image: Abhinav,
      description: 'Dedicated to creating responsive user interfaces, optimizing performance, and enhancing user experiences with modern web technologies'
    },
    {
      name: 'Dr. Kanu Goel',
      role: 'Mentor',
      linkedIn: '#',
      github: '#',
      image: Kanu,
      description: 'Backend engineer focused on developing robust server-side applications, managing databases, and ensuring seamless integration with frontend technologies'
    },
    {
      name: 'Pushkar Garg',
      role: 'AI engineer',
      linkedIn: '#',
      github: '#',
      image: Pushkar,
      description: 'AI engineer dedicated to designing and implementing intelligent systems using machine learning, deep learning, and natural language processing techniques'
    },
  ];

  return (
    <div>
      <Navbar />
      <div className="landing-container" id="home">
        <h1 className="gradient-heading">AI Driven Chest X-Ray Analysis</h1>
        <h1 className="typing-effect">
          <TypeAnimation
            sequence={[
              'Innovative.', 1000,
              'Creative.', 1000,
              'Reliable.', 1000,
              'Efficient.', 1000,
              'Future-ready.', 1000,
            ]}
            wrapper="span"
            cursor={true}
            repeat={0}
            style={{ fontSize: '100px' }}
          />
        </h1>

        {/* Add the personalized text here */}
        <h6 className="sub-heading" style={{ fontSize: '2.5rem', marginTop: '60px', color: 'black' }}>
          Preliminary Report Generation
        </h6>
      </div>

      {/* New Section with Four Parts in a Grid */}
      <div className="features-container">
        <Grid container spacing={4} justifyContent="center" id="about">
          {[
            {
              title: 'Disease Prediction from X-rays',
              description:
                'Upload chest X-ray images, and our AI model will detect diseases like pneumonia, tuberculosis, and lung cancer with precision and speed.',
              icon: <UploadFileIcon style={{ fontSize: '2.5rem', color: 'black' }} />,
            },
            {
              title: 'Preliminary Report Generation',
              description:
                'Get detailed diagnostic reports automatically generated from X-ray analysis, offering key insights into potential conditions.',
              icon: <BoltIcon style={{ fontSize: '2.5rem', color: 'black' }} />,
            },
            {
              title: 'Recommended Diagnostic Questions',
              description:
                'Receive intelligent follow-up questions based on detected diseases, along with considerations for age and gender, to streamline patient evaluation.',
              icon: <VisibilityIcon style={{ fontSize: '2.5rem', color: 'black' }} />,
            },
            {
              title: 'Interactive Frontend',
              description:
                'Engage with a user-friendly platform to upload X-rays, access results, and explore diagnostic recommendations effortlessly.',
              icon: <HeadsetIcon style={{ fontSize: '2.5rem', color: 'black' }} />,
            },
          ].map((feature, index) => (
            <Grid item xs={12} sm={6} md={3} key={index}>
              <div className="feature">
                {feature.icon}
                <Typography variant="h5" className="feature-title">
                  {feature.title}
                </Typography>
                <Typography variant="body2" className="feature-description">
                  {feature.description}
                </Typography>
              </div>
            </Grid>
          ))}
        </Grid>
      </div>

      {/* Add the RoundedButton below the feature box */}
      <div style={{ marginBottom: '50px', textAlign: 'center' }}>
        <RoundedButton routeLink="/upload" label="Try X-Ray Image Analysis" />
      </div>

      <div style={{ textAlign: 'center', marginTop: '40px', marginBottom: '20px' }}>
        <h2 style={{ fontSize: '2.5rem', fontWeight: 'bold', color: 'black' }}>
          The People Behind the Magic
        </h2>
      </div>
      {/* Grid for team member cards */}
      <div className="team-container">
        <Grid container spacing={3} justifyContent="center" id="team">
          {teamMembers.map((member, index) => (
            <Grid item xs={12} sm={6} md={4} key={index}>
              <Card>
                <CardContent>
                  {/* Member Image */}
                  <img
                    src={member.image}
                    alt={member.name}
                    style={{ width: '100%', borderRadius: '8px' }}
                  />
                  <Typography
                    variant="h5"
                    component="div"
                    style={{ marginTop: '10px', textAlign: 'center' }}
                  >
                    {member.name}
                  </Typography>
                  <Typography
                    variant="body2"
                    color="text.secondary"
                    style={{ textAlign: 'center' }}
                  >
                    {member.role}
                  </Typography>
                  <Typography
                    variant="body2"
                    style={{ marginTop: '5px', textAlign: 'center' }}
                  >
                    {member.description}
                  </Typography>
                  {/* Links for LinkedIn and GitHub */}
                  <div
                    style={{
                      marginTop: '10px',
                      display: 'flex',
                      justifyContent: 'center',
                    }}
                  >
                    <IconButton
                      color="primary"
                      onClick={() => window.open(member.linkedIn, '_blank')}
                      aria-label="LinkedIn"
                    >
                      <LinkedInIcon />
                    </IconButton>
                    <IconButton
                      color="primary"
                      onClick={() => window.open(member.github, '_blank')}
                      aria-label="GitHub"
                    >
                      <GitHubIcon />
                    </IconButton>
                  </div>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </div>
    </div>
  );

};

export default LandingPage;