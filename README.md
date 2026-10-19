# ThreatMeter AI 🛡️
### Machine Learning for SMS Spam and Email Phishing Detection

ThreatMeter AI is a web-based cybersecurity project designed to help users assess suspicious SMS messages and phishing emails using machine-learning models. It combines a simple web interface with a Python backend to provide predictions and safety recommendations.

The project began as part of **CyberCup 6.0** and is being developed further as a long-term learning and portfolio project.

> **Project status:** In development. SMS and Email detection are the current focus. URL detection and image-based analysis are planned features.

## Features

### Currently implemented
- **SMS/Message Detection:** Analyzes submitted message text for potential spam or fraudulent content.
- **Email Phishing Detection:** Analyzes submitted email text for potential phishing attempts.
- **Prediction Results:** Returns classification results and score-related information.
- **Safety Recommendations:** Provides practical guidance to help users respond cautiously to suspicious communications.
- **Web Interface:** Allows users to submit text and view analysis results.
- **REST API:** Uses FastAPI endpoints to connect the frontend with the detection models.

### Planned
- **URL Detection:** A dedicated engine for analyzing suspicious website URLs.
- **OCR and Image Analysis:** Extracting text from screenshots and using it in the detection workflow.
- **Browser Extension:** Bringing ThreatMeter's detection capabilities into desktop browsing.
- **Mobile Application:** Exploring Android and iOS access to the detection engines.
- **Improved Evaluation:** Testing on broader, unseen datasets and systematically measuring model performance.

## Technology Stack

| Technology | Purpose |
|---|---|
| HTML, CSS, JavaScript | Frontend interface |
| Python | Backend and detection logic |
| FastAPI | REST API and request validation |
| scikit-learn | Machine-learning model support |
| joblib | Loading saved model files |
| Swagger UI | Interactive API testing during development |

## Architecture

ThreatMeter AI uses a frontend–backend architecture.

```text
User
  |
  v
Web Interface
(HTML, CSS, JavaScript)
  |
  v
FastAPI Backend
  |
  +--------------------+
  |                    |
  v                    v
SMS Detector       Email Detector
  |                    |
  v                    v
SMS Model          Email Model
  |                    |
  +---------+----------+
            |
            v
     Prediction Result
            |
            v
   Results and Safety Advice
```

The frontend collects the user's input and sends it to the backend. FastAPI routes the request to the appropriate detector, which uses its saved model to produce a prediction. The backend returns a structured response for the frontend to display.

## Project Structure

The project is organized approximately as follows:

```text
ThreatMeterFinal/
├── backend/
│   ├── main.py
│   ├── message_detector.py
│   ├── email_detector.py
│   ├── sms_message_model.joblib
│   ├── threatmeter_email_model_clean_v1.joblib
│   └── other required backend files
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
├── requirements.txt
├── README.md
└── .gitignore
```

The exact structure may differ slightly depending on the final version. Keep all model files and Python modules required by the detectors.

## Running Locally

### Prerequisites
- Python installed on your computer
- The required Python packages
- The trained model files used by the SMS and Email detectors

### 1. Open the project

Extract or clone the repository and open the project root in Visual Studio Code.

### 2. Install dependencies

```bash
py -m pip install -r requirements.txt
```

On systems where `python` is configured correctly, you can use `python -m pip` instead.

### 3. Start the backend

From the project root:

```bash
py -m uvicorn backend.main:app --reload
```

The backend should be available at:

- API: `http://127.0.0.1:8000`
- Interactive API documentation: `http://127.0.0.1:8000/docs`

### 4. Start the frontend

Open a second terminal in the project root:

```bash
py -m http.server 5500
```

If the HTML file is inside the `frontend` directory, open:

`http://127.0.0.1:5500/frontend/`

If your frontend files are arranged differently, adjust the URL to match their location.

### 5. Test the detection endpoints

- `POST /analyze` — SMS/message detection
- `POST /analyze-email` — Email phishing detection

Use the interactive API documentation to submit test inputs and inspect the responses.

## Model Evaluation and Limitations

Machine-learning predictions depend on the training data and the content being analyzed. The system may produce false positives or false negatives, and performance on training data does not necessarily reflect performance on unseen messages.

ThreatMeter AI is a cybersecurity assistance and awareness project, not a guarantee that a message is safe or fraudulent. Users should independently verify suspicious requests before clicking links, responding, or sharing sensitive information.

Model performance should be reported using appropriate evaluation metrics and clearly defined test data. No claim of perfect accuracy is made.

## Roadmap

1. Improve and evaluate the SMS, Email, and URL detection engines.
2. Integrate OCR for text extraction from screenshots and other images.
3. Develop a browser extension that uses the detection services.
4. Explore Android and iOS applications.
5. Continue testing, documenting, and improving reliability.

## Contributing and Development

ThreatMeter AI is an evolving project. Development priorities include reproducible testing, reliable model integration, clear documentation, and honest evaluation of limitations.

If you explore or extend the project, keep credentials and private information out of the repository, preserve the trained models required for inference, and document any new dependencies.

## Acknowledgement

Built as part of our learning journey through **CyberCup 6.0**, with the aim of continuing development beyond the competition.

---

**ThreatMeter AI — Detect suspicious messages. Think before you trust.**
