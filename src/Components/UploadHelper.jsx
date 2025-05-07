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
  const [xRayFile, setXrayFile] = useState("");
  const [CBCFile, setCBCFile] = useState("");
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
  const [highestProbablities, setHighestProbablities] = useState([]);
  const [mappedData, setMappedData] = useState([]);
  const [generatedLink, setGeneratedLink] = useState(null);


  // Function to handle image upload with additional fields
  const handleXrayFileChange = (info) => {
    if (info.file.status !== 'removed') {
      // Ensure the file is only set if status is not 'removed'
      setXrayFile(info.file.originFileObj || info.file);
      console.log("Selected file:", info.file.originFileObj || info.file); // Debugging
    }
  };

  // Function to handle image upload with additional fields
  const handleCBCFileChange = (info) => {
    if (info.file.status !== 'removed') {
      // Ensure the file is only set if status is not 'removed'
      setCBCFile(info.file.originFileObj || info.file);
      console.log("Selected file:", info.file.originFileObj || info.file); // Debugging
    }
  };
  

  const handleUpload = async () => {
    if (!xRayFile) {
      message.warning("Please complete all fields before submitting.");
      return;
    }
    // debugger;
    const formData = new FormData();
    const CBCformData = new FormData();
    formData.append('file', xRayFile);
    formData.append('age', age);
    formData.append('gender', gender);
    formData.append('weight', weight);
    formData.append('height', height);
    formData.append('name', name);
    CBCformData.append('file', CBCFile);
    let ragRequestData = {
      "age" : age,
      "gender" : gender,
      "top_probabilities": []
    };
    try {
      const response = await axios.post('http://localhost:5000/cnn', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      console.log(response);
      
      if (response.status === 201) {
        const probabilities = response.data.predictions; // Assuming response contains probabilities array
        console.log(probabilities);
        message.success('X-Ray File uploaded successfully!');
        setDynamicNumbers(probabilities);
  
        // Step 2: Extract top 3 probabilities with disease names
        const topProbabilities = Object.entries(probabilities) // Convert object to array of [key, value] pairs
        .map(([disease, probability]) => ({ disease, probability })) // Map to an array of objects
        .sort((a, b) => b.probability - a.probability) // Sort by probability in descending order
        .slice(0, 3) // Take top 3
        .map(item => ({ [item.disease]: item.probability })); // Convert to key-value pairs
        console.log(topProbabilities)
        setHighestProbablities(topProbabilities)
        ragRequestData["top_probabilities"] = topProbabilities
        console.log(ragRequestData);

      }

      // Running both APIs in parallel
      const [CBC_Response, ragResponse] = await Promise.all([
        axios.post('http://localhost:5000/analyze-cbc', CBCformData),
        axios.post('http://localhost:5000/rag1', ragRequestData)
      ]);

      if (ragResponse.status === 200) {
        message.success('Data processed successfully!');
        console.log(ragResponse.data);
        setDiseaseQuestions(ragResponse.data); // Update questions
      }

      if(CBC_Response.status === 200){
        const responseData = response.data; // Assuming response contains probabilities array
        // localStorage.setItem('CBC_Data', JSON.stringify(responseData));
        console.log(responseData);
        message.success('CBC File uploaded successfully!');
      }

    } catch (error) {
      message.error('Failed');
      console.error(error);
    }
  };

  useEffect(() => {
    // Initialize responses once diseaseQuestions are available
    if (Object.keys(diseaseQuestions).length > 0) {
      const initialResponses = {};
      Object.entries(diseaseQuestions).forEach(([disease, questions]) => {
        initialResponses[disease] = questions.map((question) => ({
          question,
          answer: "", // Default empty answer
        }));
      });
      setResponses(initialResponses);
    }
  }, [diseaseQuestions]);

  
  // Function to handle submission of disease responses
  const handleSubmitResponses = async () => {
    try {
      const TEMP_DIR = './temp';
      const generateFilePath = (fileName) => {
        return `${TEMP_DIR}/${fileName}`;
      };
      const filePath = generateFilePath(xRayFile.name);
      console.log(filePath);
      const payload = {
        "top_diseases": highestProbablities,
        "name" : name,
        "age" : age,
        "gender" : gender,
        "height" : height,
        "weight" : weight,
        "question_answers" : responses, // Directly pass the structured `responses`
        "image_path" : filePath
      };
    
      console.log("Payload to submit:", payload);
      const response = await axios.post('http://localhost:5000/rag2', payload );
      if (response.status === 200 && response.data.pdf_link) {
        setGeneratedLink(response.data.pdf_link); // Save the link from the server
        console.log(generatedLink);
        message.success("Responses submitted successfully!");
      } else {
        message.warning("Submission succeeded but no link was provided.");
      }
    } catch (error) {
      message.error('Failed to submit responses.');
      console.error(error);
    }
  };

  // Function to handle response input change
  const handleResponseChange = (disease, questionIndex, value) => {
    setResponses((prevResponses) => ({
      ...prevResponses,
      [disease]: prevResponses[disease].map((qa, idx) =>
        idx === questionIndex ? { ...qa, answer: value } : qa
      ),
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
            <Form.Item label="Upload Chest X-Ray Image">
              <Upload
                // beforeUpload={() => false}  // Prevent auto-upload to manage manually
                onChange={handleXrayFileChange}  // Set the file to state on file change
                showUploadList={false}       // Hide the default file list if not needed
                accept="image/*"             // Accept only images (optional)
              >
                <Button icon={<UploadOutlined />}>Click to Upload</Button>
              </Upload>
            </Form.Item>
            {xRayFile && (
              <div style={{ marginTop: '8px', fontWeight: 'bold', color: '#555' }}>
                Selected file: {xRayFile.name}
              </div>
            )}
            <Form.Item label="Upload CBC Report PDF">
              <Upload
                // beforeUpload={() => false}  // Prevent auto-upload to manage manually
                onChange={handleCBCFileChange}  // Set the file to state on file change
                showUploadList={false}       // Hide the default file list if not needed
                accept="application/pdf"             // Accept only images (optional)
              >
                <Button icon={<UploadOutlined />}>Click to Upload</Button>
              </Upload>
            </Form.Item>
            {CBCFile && (
              <div style={{ marginTop: '8px', fontWeight: 'bold', color: '#555' }}>
                Selected file: {CBCFile.name}
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
            <Form.Item label="Upload Chest X-Ray Image">
              <Upload
                // beforeUpload={() => false}  // Prevent auto-upload to manage manually
                onChange={handleXrayFileChange}  // Set the file to state on file change
                showUploadList={false}       // Hide the default file list if not needed
                accept="image/*"             // Accept only images (optional)
              >
                <Button icon={<UploadOutlined />}>Click to Upload</Button>
              </Upload>
            </Form.Item>
            {xRayFile && (
              <div style={{ marginTop: '8px', fontWeight: 'bold', color: '#555' }}>
                Selected file: {xRayFile.name}
              </div>
            )}
            <Form.Item label="Upload CBC Report PDF">
              <Upload
                // beforeUpload={() => false}  // Prevent auto-upload to manage manually
                onChange={handleCBCFileChange}  // Set the file to state on file change
                showUploadList={false}       // Hide the default file list if not needed
                accept="application/pdf"             // Accept only images (optional)
              >
                <Button icon={<UploadOutlined />}>Click to Upload</Button>
              </Upload>
            </Form.Item>
            {CBCFile && (
              <div style={{ marginTop: '8px', fontWeight: 'bold', color: '#555' }}>
                Selected file: {CBCFile.name}
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
              {(responses[disease] || []).map((qa, index) => ( // Add default fallback to empty array
                <Row key={index} align="middle" style={{ marginBottom: '8px' }}>
                  {/* Display the question */}
                  <Col span={16}>
                    <Text>{qa.question}</Text>
                  </Col>
                  {/* Display the corresponding TextArea */}
                  <Col span={8}>
                    <TextArea
                      placeholder="Type your response here"
                      onChange={(e) =>
                        handleResponseChange(disease, index, e.target.value) // Update the specific response
                      }
                      value={qa.answer} // Bind to the specific answer
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
        {generatedLink && (
          <div
            style={{
              marginTop: "20px",
              padding: "10px",
              border: "1px solid #d9d9d9",
              borderRadius: "4px",
              backgroundColor: "#f6f6f6",
            }}
          >
            <p style={{ margin: 0, fontSize: "16px", color: "#333" }}>
              <strong>Generated Link:</strong>
            </p>
            <a
              href={generatedLink}
              target="_blank"
              rel="noopener noreferrer"
              style={{
                display: "inline-block",
                marginTop: "5px",
                color: "#1890ff",
                textDecoration: "underline",
              }}
            >
              {generatedLink}
            </a>
          </div>
        )}
        </Content>
      </Layout>
    </Layout>
  );
};

export default UploadHelper;
