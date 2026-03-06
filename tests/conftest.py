import epicevents.models.client 
import epicevents.models.contract
import epicevents.models.event 
import epicevents.models.collaborator  
import epicevents.models.role 

import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from epicevents.models.base import Base
from epicevents.db.session import SessionLocal

# Set the JWT secret key for the tests
os.environ["EPICEVENTS_SECRET"] = "test-secret-test-secret-test-secret"

@pytest.fixture
def session():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    s = SessionLocal()
    try:
        yield s
    finally:
        s.close()   