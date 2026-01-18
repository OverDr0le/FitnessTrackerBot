from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, BigInteger, String, Date, UniqueConstraint, func, ForeignKey
from datetime import date


class Base(DeclarativeBase):
    date: Mapped[date] = mapped_column(Date, server_default= func.current_date())

class User(Base):
    __tablename__='users'

    telegram_id: Mapped[int] = mapped_column(BigInteger,primary_key=True, unique= True)
    height: Mapped[int] = mapped_column(Integer, nullable= False)
    weight: Mapped[int] = mapped_column(Integer, nullable=False)
    sex: Mapped[str] = mapped_column(String(50), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable = False)
    city: Mapped[str] = mapped_column(String(50), nullable = False)
    calories_goal: Mapped[int] = mapped_column(Integer, nullable= False)
    water_goal: Mapped[int] = mapped_column(Integer,nullable=False)
    
    daily_stats: Mapped[list["UserDailyStats"]] = relationship(
        back_populates = "user",
        cascade = "all, delete-orphan"
    )

class UserDailyStats(Base):
    __tablename__ = "user_daily_stats"

    id: Mapped[int] = mapped_column(Integer,primary_key = True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(
        ForeignKey("users.telegram_id", ondelete="CASCADE"),
        nullable=False
    )
    calories_consumed: Mapped[int] = mapped_column(Integer,default = 0)
    calories_burned: Mapped[int] = mapped_column(Integer, default = 0)
    water_consumed: Mapped[int] = mapped_column(Integer, default = 0)

    user: Mapped["User"] = relationship(
        back_populates="daily_stats"
    )

    __table_args__ = (
        UniqueConstraint("telegram_id","date"),
    )
