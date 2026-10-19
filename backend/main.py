from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging

from backend.message_detector import classify_message
from backend.email_detector import classify_email
from backend.url_detector import classify_url


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="ThreatMeter AI Detector")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


class MessageRequest(BaseModel):
    message: str


class EmailRequest(BaseModel):
    text: str


class URLRequest(BaseModel):
    url: str


@app.get("/")
def home():
    return {"status": "ThreatMeter backend is running"}


@app.post("/analyze")
def analyze(request: MessageRequest):
    if not request.message.strip():
        raise HTTPException(
            status_code=400,
            detail="Please enter a message.",
        )

    try:
        result = classify_message(request.message)

        return {
            "status": result["label"],
            "label": result["label"].upper(),
            "score": result["score"],
            "confidence": result["confidence"],
            "spam_probability": result["spam_probability"],
            "summary": result["explanation"],
            "indicators": [],
            "recommendations": [
                "Verify the sender before acting on an unexpected message.",
                "Never share passwords or one-time codes in response to an unexpected message.",
                "Treat this prediction as an estimate, not a guarantee of safety.",
            ],
        }
    except (ValueError, TypeError) as error:
        raise HTTPException(status_code=400, detail=str(error))
    except Exception:
        logger.exception("SMS analysis failed")
        raise HTTPException(
            status_code=500,
            detail="Message analysis failed. Check the backend terminal.",
        )


@app.post("/analyze-email")
def analyze_email(request: EmailRequest):
    if not request.text.strip():
        raise HTTPException(
            status_code=400,
            detail="Please enter email text.",
        )

    try:
        result = classify_email(request.text)

        logger.info(
            "Email prediction: label=%s, score=%s, confidence=%s",
            result.get("label"),
            result.get("score"),
            result.get("confidence"),
        )

        return {
            "status": result["label"],
            "label": result["label"].upper(),
            "score": result["score"],
            "confidence": result["confidence"],
            "phishing_probability": result["phishing_probability"],
            "summary": result["explanation"],
            "indicators": [],
            "recommendations": [
                "Verify the sender's address before responding.",
                "Do not open suspicious links or attachments.",
                "Never share passwords or one-time codes in response to unexpected emails.",
                "Verify job offers through the organization's official careers website.",
                "Treat this prediction as an estimate, not a guarantee of safety.",
            ],
        }

    except (ValueError, TypeError) as error:
        raise HTTPException(status_code=400, detail=str(error))
    except Exception:
        logger.exception("Email analysis failed")
        raise HTTPException(
            status_code=500,
            detail="Email analysis failed. Check the backend terminal.",
        )


@app.post("/analyze-url")
def analyze_url(request: URLRequest):
    if not request.url.strip():
        raise HTTPException(
            status_code=400,
            detail="Please enter a URL.",
        )

    try:
        result = classify_url(request.url)

        return {
            "status": result["label"],
            "label": result["label"].upper(),
            "score": result["score"],
            "confidence": max(
                result["phishing_probability"],
                result["legitimate_probability"],
            ),
            "phishing_probability": result["phishing_probability"],
            "summary": result["explanation"],
            "indicators": [],
            "recommendations": [
                "Avoid entering passwords or payment details if the URL appears suspicious.",
                "Check the website address carefully before proceeding.",
                "Treat this prediction as an estimate, not a guarantee of safety.",
            ],
        }

    except (ValueError, TypeError) as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )
    except Exception:
        logger.exception("URL analysis failed")
        raise HTTPException(
            status_code=500,
            detail="URL analysis failed. Check the backend terminal.",
        )
