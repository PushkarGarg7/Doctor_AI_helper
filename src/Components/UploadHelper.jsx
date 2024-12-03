import React, { useState, useEffect } from 'react';
import { Layout, List, Typography, Upload, Button, message, Form, Input, Select, Drawer, Row, Col } from 'antd';
import { UploadOutlined, MenuOutlined } from '@ant-design/icons';
import axios from 'axios';
import '../Styles/UploadHelper.css';

const { Sider, Content } = Layout;
const { Text } = Typography;
const { Option } = Select;
const { TextArea } = Input;

const diseases = [
  "Atelectasis","Consolidation","Infiltration", "Pneumothorax","Edema", "Emphysema", "Fibrosis", 
  "Effusion", "Pneumonia", "Pleural_thickening","Cardiomegaly", "Nodule Mass", "Hernia"
];

const UploadHelper = () => {
  const [file, setFile] = useState("");
  const [dynamicNumbers, setDynamicNumbers] = useState([]);
  const [collapsed, setCollapsed] = useState(false);
  const [drawerVisible, setDrawerVisible] = useState(false);
  const [age, setAge] = useState('');
  const [gender, setGender] = useState('');
  const [name, setName] = useState('');
  const [weight, setWeight] = useState('');
  const [height, setHeight] = useState('');
  const [diseaseQuestions, setDiseaseQuestions] = useState({}); // Store questions from server response
  const [responses, setResponses] = useState({}); // Store user responses to questions
  const [mappedData, setMappedData] = useState([]);

  // Function to handle image upload with additional fields
  const handleFileChange = (info) => {
    if (info.file.status !== 'removed') {
      // Ensure the file is only set if status is not 'removed'
      setFile(info.file.originFileObj || info.file);
      console.log("Selected file:", info.file.originFileObj || info.file); // Debugging
    }
  };
  

  const handleUpload = async () => {
    if (!file) {
      message.warning("Please complete all fields before submitting.");
      return;
    }
    debugger;
    const formData = new FormData();
    formData.append('file', file);
    formData.append('age', age);
    formData.append('gender', gender);
    formData.append('weight', weight);
    formData.append('height', height);
    formData.append('name', name);
    try {
      const response = await axios.post('http://localhost:5000/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      console.log(response);
      // setDynamicNumbers(response.data.predictions);
      // if(response.status === 201){
      //   message.success('File uploaded successfully!');
      //   setTimeout(() => {
      //     setDynamicNumbers(response.data.disease_data.disease_probabilities); // Update dynamic numbers from server response
      //     // setDiseaseQuestions(response.data.disease_data.questions);
      //   }, 1000);
      // }
      if (response.status === 201) {
        const probabilities = response.data.disease_data.disease_probabilities; // Assuming response contains probabilities array
        console.log(probabilities);
        message.success('File uploaded successfully!');
        setTimeout(() => {
          setDynamicNumbers(probabilities); // Update dynamic numbers from server response
          // setDiseaseQuestions(response.data.disease_data.questions);
        }, 1000);
  
        // Step 2: Extract top 3 probabilities with disease names
        const topProbabilities = Object.entries(probabilities) // Convert object to array of [key, value] pairs
        .map(([disease, probability]) => ({ disease, probability })) // Map to an array of objects
        .sort((a, b) => b.probability - a.probability) // Sort by probability in descending order
        .slice(0, 3) // Take top 3
        .map(item => ({ [item.disease]: item.probability })); // Convert to key-value pairs
        console.log(topProbabilities)
        // Step 3: Call /rag1 with age, gender, and top probabilities
        const ragRequestData = {
        age,
        gender,
        top_probabilities: topProbabilities
        };
        console.log(ragRequestData);
        const ragResponse = await axios.post('http://localhost:5000/rag1', ragRequestData);

        console.log(ragResponse);
        if (ragResponse.status === 200) {
          message.success('Data processed successfully!');
          setDiseaseQuestions(ragResponse.data); // Update questions
        }
      }

    } catch (error) {
      message.error('Failed');
      console.error(error);
    }
  };


  // Function to handle submission of disease responses
  const handleSubmitResponses = async () => {
    try {
      const response = await axios.post('http://localhost:5000/responses', { responses });
      message.success('Responses submitted successfully!');
    } catch (error) {
      message.error('Failed to submit responses.');
      console.error(error);
    }
  };

  // Function to handle response input change
  const handleResponseChange = (disease, questionIndex, value) => {
    setResponses((prevResponses) => ({
      ...prevResponses,
      [disease]: {
        ...prevResponses[disease], // Preserve existing responses for the disease
        [questionIndex]: value, // Update the specific question's response
      },
    }));
  };
  
  useEffect(() => {
    const newMappedData = diseases.map((name) => ({
      name,
      number: dynamicNumbers[name] || '-',
    }));
    setMappedData(newMappedData);
  }, [dynamicNumbers]); // Dependency on dynamicNumbers to trigger re-computation



  return (
    <Layout style={{ minHeight: '100vh' }}>
      {/* Toggle button for small screens */}
      <Button
        icon={<MenuOutlined />}
        onClick={() => setDrawerVisible(true)}
        style={{ position: 'fixed', top: 16, left: 16, zIndex: 1000, display: collapsed ? 'block' : 'none' }}
      />
      
      <Drawer
        title="Sidebar"
        placement="left"
        onClose={() => setDrawerVisible(false)}
        visible={drawerVisible}
        bodyStyle={{ padding: 0 }}
        destroyOnClose = {false}
      >
        <div style={{ padding: '16px', backgroundColor: '#f9fafb' }}>
          <Form layout="vertical">
            <Form.Item label="Upload Image">
            <Upload
              beforeUpload={() => false}  // Prevents auto-upload
              onChange={handleFileChange}  // Save file to state on change
              showUploadList={false}       // Hide default file list
              accept='image/*'
            >
              <Button icon={<UploadOutlined />}>Click to Upload</Button>
            </Upload>
            </Form.Item>
            {file && (
              <div style={{ marginTop: '8px', fontWeight: 'bold', color: '#555' }}>
                Selected file: {file.name}
              </div>
            )}
            <Form.Item label="Enter Your Age">
              <Input
                placeholder="Enter age"
                type="number"
                value={age}
                onChange={(e) => setAge(e.target.value)}
              />
            </Form.Item>
            <Form.Item label="Select Gender">
              <Select
                placeholder="Select your gender"
                value={gender || null}
                onChange={(value) => setGender(value)}
              >
                <Option value="male">Male</Option>
                <Option value="female">Female</Option>
                <Option value="other">Other</Option>
              </Select>
            </Form.Item>
            <Form.Item>
              <Button
                type="primary"
                onClick={handleUpload}
                style={{ width: '100%' }}
              >
                Submit
              </Button>
            </Form.Item>
          </Form>
          <h3 style={{ textAlign: 'center' }}>Disease Probablities</h3>
          <List
            dataSource={mappedData}
            renderItem={(item) => (
              <List.Item>
                <Text style={{ fontWeight: 500 }}>{item.name}</Text>
                <Text style={{ float: 'right', fontWeight: 'bold' }}>{item.number}</Text>
              </List.Item>
            )}
          />
        </div>
      </Drawer>

      <Sider
        width="20%"
        collapsible
        collapsed={collapsed}
        onCollapse={setCollapsed}
        style={{
          background: '#f0f2f5',
          padding: '16px',
          overflow: 'auto',
          boxShadow: '2px 0 5px rgba(0,0,0,0.1)',
          display: collapsed ? 'none' : 'block'
        }}
        breakpoint="lg"
        collapsedWidth="0"
      >
        <div style={{ marginBottom: '24px' }}>
          <Form layout="vertical">
            <Form.Item label="Upload Image">
              <Upload
                // beforeUpload={() => false}  // Prevent auto-upload to manage manually
                onChange={handleFileChange}  // Set the file to state on file change
                showUploadList={false}       // Hide the default file list if not needed
                accept="image/*"             // Accept only images (optional)
              >
                <Button icon={<UploadOutlined />}>Click to Upload</Button>
              </Upload>
            </Form.Item>
            {file && (
              <div style={{ marginTop: '8px', fontWeight: 'bold', color: '#555' }}>
                Selected file: {file.name}
              </div>
            )}
            <Form.Item label="Enter Your Name">
              <Input
                placeholder="Enter Name"
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
            </Form.Item>
            <Form.Item label="Enter Your Age">
              <Input
                placeholder="Enter age"
                type="number"
                value={age}
                onChange={(e) => setAge(e.target.value)}
              />
            </Form.Item>
            <Form.Item label="Enter Your Height (Cm)">
              <Input
                placeholder="Enter Height"
                type="number"
                value={height}
                onChange={(e) => setHeight(e.target.value)}
              />
            </Form.Item>
            <Form.Item label="Enter Your Weight (Kg)">
              <Input
                placeholder="Enter Weight"
                type="number"
                value={weight}
                onChange={(e) => setWeight(e.target.value)}
              />
            </Form.Item>
            <Form.Item label="Select Gender">
              <Select
                placeholder="Select your gender"
                value={gender || null}
                onChange={(value) => setGender(value)}
              >
                <Option value="male">Male</Option>
                <Option value="female">Female</Option>
                <Option value="other">Other</Option>
              </Select>
            </Form.Item>
            <Form.Item>
              <Button
                type="primary"
                onClick={handleUpload}
                style={{ width: '100%' }}
              >
                Submit
              </Button>
          </Form.Item>
          </Form>
        </div>
        <h3 style={{ textAlign: 'center' }}>Disease Probablities</h3>
        <List
          dataSource={mappedData}
          renderItem={(item) => (
            <List.Item>
              <Text style={{ fontWeight: 500 }}>{item.name}</Text>
              <Text style={{ float: 'right', fontWeight: 'bold' }}>{item.number}</Text>
            </List.Item>
          )}
        />
      </Sider>

      <Layout>
        <Content
          style={{
            margin: '24px 16px 0',
            // padding: 24,
            background: '#fff',
            borderRadius: '8px',
          }}
        >
        <h1>Disease Questions</h1>
        <Row gutter={[16, 16]}>
          {Object.entries(diseaseQuestions).map(([disease, questions]) => (
            <Col xs={24} key={disease}>
              <h2 style={{ marginBottom: '8px', fontSize: '20px', color: '#333' }}>
                {disease}
              </h2> {/* Disease heading */}
              {questions.map((question, index) => (
                <Row key={index} align="middle" style={{ marginBottom: '8px' }}>
                  {/* Display the question */}
                  <Col span={16}>
                    <Text>{question}</Text>
                  </Col>
                  {/* Display the corresponding TextArea */}
                  <Col span={8}>
                    <TextArea
                      placeholder="Type your response here"
                      onChange={(e) =>
                        handleResponseChange(disease, index, e.target.value) // Add index for question-specific response
                      }
                      value={responses[disease]?.[index] || ''} // Use index for the specific response
                      rows={1}
                      style={{
                        width: '100%',
                        borderRadius: '4px',
                        border: '1px solid #d9d9d9',
                        boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
                        transition: 'border-color 0.2s',
                      }}
                    />
                  </Col>
                </Row>
              ))}
            </Col>
          ))}
        </Row>

        <Button
          type="primary"
          onClick={handleSubmitResponses}
          style={{ marginTop: '16px' }}
        >
          Submit Responses
        </Button>
        </Content>
      </Layout>
    </Layout>
  );
};

export default UploadHelper;
