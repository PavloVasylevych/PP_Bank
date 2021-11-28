from sqlalchemy import *
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, sessionmaker, scoped_session

engine = create_engine('mysql+pymysql://root:PavloVasylevych@localhost:3306/mydb')
SessionFactory = sessionmaker(bind=engine)
Session = scoped_session(SessionFactory)
Base=declarative_base()
metadata=Base.metadata

class Bank(Base):
    __tablename__='Bank'
    bank_id = Column(Integer, primary_key=True)
    name = Column(String(45))
    balance = Column(Integer, default = 570000)


class User(Base):
    __tablename__ = 'User'
    id = Column(Integer, primary_key=True)
    username = Column(String(45))
    password = Column(String(200))
    ClientName = Column(String(45))
    firstName = Column(String(45))
    lastName = Column(String(45))
    status = Column(String(45))



class Credit(Base):
    __tablename__ = 'Credit'
    id = Column(Integer, primary_key=True)
    id_borrower = Column(Integer, ForeignKey('User.id'))
    id_bank = Column(Integer, ForeignKey('Bank.bank_id'))
    loan_status = Column(Boolean, default=false)
    loan_date = Column(String(45))
    loan_amount = Column(Integer)
    interest_rate = Column(Integer, default=30)
    User = relationship("User")
    Bank = relationship("Bank")
