from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, BigInteger, String, DateTime, UniqueConstraint, func, ForeignKey

class Base(DeclarativeBase):
    created_at: Mapped[DateTime] = mapped_column(DateTime, default= func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now(),onupdate=func.now())

class User(Base):
    __tablename__='users'

    telegram_id: Mapped[int] = mapped_column(BigInteger,primary_key=True, unique= True)
    height: Mapped[int] = mapped_column(Integer, nullable= False)
    weight: Mapped[int] = mapped_column(Integer, nullable=False)
    sex: Mapped[str] = mapped_column(String(50), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable = False)
    city: Mapped[str] = mapped_column(String(50), nullable = False)
    daily_stats: Mapped[list["UserDailyStats"]] = relationship(
        back_populates = "user",
        cascade = "all, delete-orphan"
    )

class UserDailyStats(Base):
    __tablename__ = "user_daily_stats"

    telegram_id: Mapped[int] = mapped_column(
        ForeignKey("users.telegram_id", ondelete="CASCADE"),
        nullable=False,
        primary_key=True
    )
    calories_goal: Mapped[int] = mapped_column(Integer, nullable= False)
    water_goal: Mapped[int] = mapped_column(Integer,nullable=False)
    calories_consumed: Mapped[int] = mapped_column(Integer,default = 0)
    calories_burned: Mapped[int] = mapped_column(Integer, default = 0)
    water_consumed: Mapped[int] = mapped_column(Integer, default = 0)

    user: Mapped["User"] = relationship(
        back_populates="daily_stats"
    )

    __table_args__ = (
        UniqueConstraint("telegram_id","created_at"),
    )
