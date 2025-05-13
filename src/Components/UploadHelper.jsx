import React, { useState, useEffect } from 'react';
import { Layout, List, Typography, Upload, Button, message, Form, Select, Drawer, Row, Col, Spin, Input, Card} from 'antd';
import { UploadOutlined, MenuOutlined } from '@ant-design/icons';
import axios from 'axios';
import '../Styles/UploadHelper.css';

const { Sider, Content } = Layout;
const { Text, Title, Paragraph} = Typography;
const { Option } = Select;
const { TextArea } = Input;

const diseases = [
'Cardiomegaly', 'Emphysema', 'Effusion', 'Hernia', 'Infiltration', 'Mass', 'Nodule', 'Atelectasis', 
'Pneumothorax', 'Pleural_Thickening', 'Pneumonia', 'Fibrosis', 'Edema', 'Consolidation'];

  
const thresholds = [ 0.450887, 0.471386, 0.488033, 0.494578, 0.545257, 0.506546, 0.478008, 0.484116,
  0.511385, 0.509026, 0.546525, 0.515503, 0.557461, 0.549326
];


const UploadHelper = () => {
  const [xRayFile, setXrayFile] = useState("");
  const [CBCFile, setCBCFile] = useState("");
  const [threshDiseases, setThreshDiseases] = useState([]);
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
  const [isQuestionsAvailaible, setIsQuestionsAvaliable] = useState(false)
  const [isAgentStarted, setIsAgentStarted] = useState(false)
  const [isTopPredictionsAvailaible, setIsTopPredictionsAvailaible] = useState(true);

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
      
      // const newCBCresponse = await axios.get('http://localhost:5000/openaicbc', {
      //   headers: { 'Content-Type': 'multipart/form-data' },
      // });
      // console.log(newCBCresponse);
      const posProbablities = response.data.positive_predictions;

      const hasTopProbs = posProbablities && Object.keys(posProbablities).length >= 1;

      if (response.status === 201) {
        const probabilities = response.data.predictions; // Assuming response contains probabilities array
        const positiveDisease = response.data.positive_diseases;
        const topProbablities = response.data.positive_predictions;

        console.log(probabilities);
        message.success('X-Ray File uploaded successfully!');
        setDynamicNumbers(probabilities);
        setThreshDiseases(positiveDisease);


        if(!hasTopProbs) {
          setIsTopPredictionsAvailaible(false);
        }
        else{
          setIsAgentStarted(true);
        }

        if(hasTopProbs){
        const topProbabilities = Object.entries(topProbablities) // Step 1: Convert dict to array
        .sort((a, b) => b[1] - a[1]) // Step 2: Sort by probability descending
        .map(([disease, probability]) => ({ [disease]: probability })); // Step 4: Format

        console.log(topProbabilities)
        setHighestProbablities(topProbabilities)
        ragRequestData["top_probabilities"] = topProbabilities
        console.log(ragRequestData);
        }
      }

      if(hasTopProbs){     
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
      }
      } 
      catch (error) {
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
      setIsAgentStarted(false);
      setIsQuestionsAvaliable(true);
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
      setIsAgentStarted(true);
      
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
        setIsAgentStarted(false);
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
    const newMappedData = diseases.map((name, index) => ({
      name,
      number: dynamicNumbers[name] || '-',
      threshold: thresholds[index],
    }));
    setMappedData(newMappedData);
  }, [dynamicNumbers]);



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
            <Form.Item label="Enter Your Height">
              <Input
                placeholder="Enter Height"
                type="number"
                value={height}
                onChange={(e) => setHeight(e.target.value)}
              />
            </Form.Item>
            <Form.Item label="Enter Your Weight">
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
          <h3 style={{ textAlign: 'center' }}>Disease Probablities</h3>
          {/* <List
            dataSource={mappedData}
            renderItem={(item) => (
              <List.Item>
                <Text style={{ fontWeight: 500 }}>{item.name}</Text>
                <Text style={{ float: 'right', fontWeight: 'bold' }}>{item.number}</Text>
              </List.Item>
            )}
          /> */}
          <List
            header={
              <div style={{ display: 'flex', fontWeight: 'bold' }}>
                <div style={{ flex: 1 }}>Disease</div>
                <div style={{ flex: 1 }}>Threshold</div>
                <div style={{ flex: 1 }}>Probability</div>
              </div>
            }
            dataSource={mappedData}
            renderItem={(item) => {
              const isHighlighted = threshDiseases.includes(item.name);
              return (
                <List.Item
                  style={{
                    backgroundColor: isHighlighted ? '#ffcccc' : 'transparent', // light red
                    padding: '8px',
                    borderRadius: '4px',
                  }}
                >
                  <div style={{ flex: 1, fontWeight: 500 }}>{item.name}</div>
                  <div style={{ width: 100, textAlign: 'right' }}>{item.threshold.toFixed(3)}</div>
                  <div style={{ width: 100, textAlign: 'right', fontWeight: 'bold' }}>{item.number}</div>
                </List.Item>
              );
            }}
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
        {/* <List
          dataSource={mappedData}
          renderItem={(item) => (
            <List.Item>
              <Text style={{ fontWeight: 500 }}>{item.name}</Text>
              <Text style={{ float: 'right', fontWeight: 'bold' }}>{item.number}</Text>
            </List.Item>
          )}
        /> */}
        <List
          header={
            <div style={{ display: 'flex', fontWeight: 'bold' }}>
              <div style={{ flex: 1 }}>Disease</div>
              <div style={{ flex: 1 }}>Threshold</div>
              <div style={{ flex: 1 }}>Probability</div>
            </div>
          }
          dataSource={mappedData}
          renderItem={(item) => {
            const isHighlighted = threshDiseases.includes(item.name);
            return (
              <List.Item
                style={{
                  backgroundColor: isHighlighted ? '#ffcccc' : 'transparent', // light red
                  padding: '8px',
                  borderRadius: '4px',
                }}
              >
                <div style={{ flex: 1, fontWeight: 500 }}>{item.name}</div>
                <div style={{ width: 100, textAlign: 'right' }}>{item.threshold.toFixed(3)}</div>
                <div style={{ width: 100, textAlign: 'right', fontWeight: 'bold' }}>{item.number}</div>
              </List.Item>
            );
          }}
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
        {!isAgentStarted && !isQuestionsAvailaible && isTopPredictionsAvailaible && (
          <Row justify="center" align="middle" style={{ minHeight: '80vh' }}>
            <Col xs={22} sm={20} md={16} lg={12}>
              <Card
                style={{
                  backgroundColor: '#e6f4ff',
                  borderRadius: '12px',
                  boxShadow: '0 4px 12px rgba(0, 80, 179, 0.1)',
                  padding: '32px',
                  textAlign: 'center',
                }}
              >
                <Title level={2} style={{ color: '#0050b3' }}>
                  Welcome to AI-Based Lung Disease Detection
                </Title>
                <Paragraph style={{ color: '#003a8c', fontSize: '16px', marginTop: '16px' }}>
                  Upload your Chest X-Ray and CBC report, along with basic body details.
                  Our AI will analyze the data and generate a preliminary diagnostic report highlighting
                  possible lung-related conditions.
                </Paragraph>
              </Card>
            </Col>
          </Row>
        )}

        {!isTopPredictionsAvailaible && (
          <div
            style={{
              backgroundColor: '#e6f7ff',
              padding: '24px',
              borderRadius: '8px',
              border: '1px solid #91d5ff',
              marginTop: '20px',
            }}
          >
            <Typography.Title level={3} style={{ color: '#1890ff' }}>
              No Disease Detected
            </Typography.Title>
            <Typography.Paragraph style={{ color: '#0050b3', fontSize: '16px' }}>
              The X-ray analysis indicates that the patient is likely free from any lung-related diseases. <br />
              No further abnormalities were detected based on the current input.
            </Typography.Paragraph>
          </div>
        )}

        {isQuestionsAvailaible &&(
        <div>
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
        </div>
      )}

        {isAgentStarted && (
          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}>
            <Spin tip="Loading" size="large">
            </Spin>
          </div>
        )}

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
