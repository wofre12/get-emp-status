from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from tenacity import retry, stop_after_attempt, wait_exponential
from .models import Base, User, Salary
from typing import List

class DataAccess:
    def __init__(self, db_url: str):
        connect_args = {"check_same_thread": False} if db_url.startswith("sqlite") else {}
        self.engine = create_engine(db_url, echo=False, future=True, connect_args=connect_args)
        self.SessionLocal = sessionmaker(bind=self.engine, autoflush=False, autocommit=False, future=True)

    def create_all(self):
        Base.metadata.create_all(self.engine)

    def get_session_factory(self):
        return self.SessionLocal

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.2, min=0.2, max=2), reraise=True)
    def get_user_by_national(self, national_number: str) -> User | None:
        with self.SessionLocal() as session:
            stmt = select(User).where(User.national_number == national_number)
            return session.execute(stmt).scalar_one_or_none()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.2, min=0.2, max=2), reraise=True)
    def get_salaries_for_user(self, user_id: int) -> List[Salary]:
        with self.SessionLocal() as session:
            stmt = select(Salary).where(Salary.user_id == user_id)
            return session.execute(stmt).scalars().all()
