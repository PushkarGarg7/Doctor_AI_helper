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
    try {
      const response = await axios.post('http://localhost:5000/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      console.log(response);
      if(response.status === 201){
        message.success('File uploaded successfully!');
        setTimeout(() => {
          setDynamicNumbers(response.data.disease_data.disease_probabilities); // Update dynamic numbers from server response
          setDiseaseQuestions(response.data.disease_data.questions);
        }, 2000);
      }
    } catch (error) {
      message.error('Failed to upload file.');
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
  const handleResponseChange = (questionIndex, value) => {
    setResponses((prevResponses) => ({
      ...prevResponses,
      [questionIndex]: value,
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
                value={gender}
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
              <h2 style={{ marginBottom: '8px', fontSize: '20px', color: '#333' }}>{disease}</h2> {/* Disease heading */}
              {/* Map through questions and display each on a new line */}
              {questions.map((question, index) => (
                <Text key={index} style={{ display: 'block', marginBottom: '4px' }}>
                  {question}
                </Text>
              ))}
              <TextArea
                placeholder="Type your response here"
                onChange={(e) => handleResponseChange(disease, e.target.value)} // Use disease name for response key
                value={responses[disease] || ''}
                rows={4}
                style={{
                  width: '80%',  // Decrease horizontal size of the textbox
                  marginTop: 8,
                  borderRadius: '4px',
                  border: '1px solid #d9d9d9',
                  boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
                  transition: 'border-color 0.2s',
                }}
              />
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
