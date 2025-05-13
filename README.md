# 🌟 Doctor AI Helper 🌟

Doctor AI Helper is a **web application** designed to assist in **medical diagnostics** by analyzing **CBC reports** and **X-ray images**. It leverages **AI models** to provide detailed insights and recommendations for healthcare professionals.

---

## 📂 Project Structure

```
Doctor_AI_helper/
├── Backend/              # Contains all backend-related files
├── public/               # Public assets for the frontend
├── src/                  # Source code for the frontend
├── .gitignore            # Git ignore file
├── package.json          # Frontend dependencies
├── README.md             # Project documentation
├── vite.config.js        # Vite configuration for React
```

---

## 🚀 Setup Instructions

### 🛠️ Backend Setup

1. Navigate to the `Backend` folder:
   ```bash
   cd Backend
   ```

2. Install all required Python libraries using `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

3. Start the backend server:
   ```bash
   python app.py
   ```

   The backend will run on [http://localhost:5000](http://localhost:5000).

---

### 🎨 Frontend Setup

1. Navigate to the root directory of the project (where `package.json` is located).

2. Install all required dependencies:
   ```bash
   npm install
   ```

3. Start the frontend development server:
   ```bash
   npm run dev
   ```

   The frontend will run on [http://localhost:5173](http://localhost:5173) (or another port if specified).

---

## 🌐 Running the Web Application

### Start the Backend:
```bash
cd Backend
python app.py
```

### Start the Frontend:
```bash
npm run dev
```

### Open your browser and navigate to:
[http://localhost:5173](http://localhost:5173)

---

## 🛠️ Technologies Used

- **Backend**: Flask, Python  
- **AI Reasoning**: CrewAI  
- **Frontend**: React.js, Vite  
- **Database**: MongoDB (configured in the backend)

### Other Tools:
- ReportLab for PDF generation  
- TensorFlow for AI models  

---

## 📝 Notes

- Ensure that Python and Node.js are installed on your system.
- The backend requires environment variables to be set in the `.env` file (e.g., database credentials, API keys).
- The frontend and backend communicate via REST APIs.

---

## 💡 Features

- **AI-Powered Diagnostics**: Analyze CBC reports and X-ray images with precision.
- **Interactive Frontend**: User-friendly interface for uploading files and viewing results.
- **Detailed Reports**: Automatically generated diagnostic reports with key insights.
- **Customizable**: Easily extendable for additional features or integrations.
