import uuid
from sqlalchemy import Column, String, DateTime, func, BigInteger, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship
from datetime import timezone, timedelta

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(
        BigInteger,
        primary_key=True,
        unique=True,
        nullable=False
    )
    notes = relationship(
        "Note",
        back_populates="user",
        cascade="all, delete-orphan"
    )


class Note(Base):
    __tablename__ = "notes"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    user_id = Column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    text = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now(),
        nullable=False)
    user = relationship(
        "User", back_populates="notes"
    )

    def formatted_time(self, tz_offset_hours: int = 3) -> str:
        """
        Возвращает строку с датой и временем
        заметки в указанном часовом поясе.
        """
        dt = self.updated_at or self.created_at
        if dt is None:
            return ""
        if dt.tzinfo:
            local_time = dt.astimezone(
                timezone(
                    timedelta(
                        hours=tz_offset_hours)
                    )
                )
        else:
            local_time = dt.replace(tzinfo=timezone.utc).astimezone(
                timezone(timedelta(hours=tz_offset_hours))
            )
        return local_time.strftime("%Y-%m-%d %H:%M")
