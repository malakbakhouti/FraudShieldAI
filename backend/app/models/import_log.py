from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base

class ImportLog(Base):
    __tablename__ = "import_logs"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    imported_by_email = Column(String, nullable=False)
    total_records = Column(Integer, default=0)
    frauds_detected = Column(Integer, default=0)
    errors = Column(Integer, default=0)
    status = Column(String, default="completed")  # completed, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
