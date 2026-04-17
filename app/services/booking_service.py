import re
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.db.models import Booking


class BookingService:
    @staticmethod
    def is_booking_intent(message: str) -> bool:
        text = message.lower()
        keywords = ["book", "schedule", "interview", "appointment"]
        return any(keyword in text for keyword in keywords)

    @staticmethod
    def extract_name(message: str) -> Optional[str]:
        match = re.search(r"name\s*[:=-]?\s*([A-Za-z ]+)", message, re.IGNORECASE)
        return match.group(1).strip() if match else None

    @staticmethod
    def extract_email(message: str) -> Optional[str]:
        match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', message)
        return match.group(0) if match else None

    @staticmethod
    def extract_date(message: str) -> Optional[str]:
        match = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", message)
        return match.group(1) if match else None

    @staticmethod
    def extract_time(message: str) -> Optional[str]:
        match = re.search(r"\b(\d{2}:\d{2})\b", message)
        return match.group(1) if match else None

    def save_booking(self, db: Session, message: str) -> str:
        name = self.extract_name(message)
        email = self.extract_email(message)
        date_str = self.extract_date(message)
        time_str = self.extract_time(message)

        if not all([name, email, date_str, time_str]):
            return (
                "I detected an interview booking request, but some details are missing. "
                "Please provide: name, email, date (YYYY-MM-DD), and time (HH:MM)."
            )

        booking = Booking(
            name=name,
            email=email,
            date=datetime.strptime(date_str, "%Y-%m-%d").date(),
            time=datetime.strptime(time_str, "%H:%M").time(),
        )

        db.add(booking)
        db.commit()
        db.refresh(booking)

        return (
            f"Interview booking saved successfully for {booking.name} on "
            f"{booking.date} at {booking.time}."
        )