from sqlalchemy import *
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker

engine = create_engine("mysql+mysqlconnector://root:qwerty@localhost/pplabs")

Base=declarative_base()
metadata=Base.metadata


class Credit(Base):
    __tablename__='credit'
    idCredit=Column(Integer, primary_key=True)
    idType = Column(Integer, ForeignKey('types_credit.idType'))
    idBorrower = Column(Integer, ForeignKey('borrower.idBorrower'))
    soum=Column(Integer)
    date_of_issue = Column(Date)
    canceled = Column(Boolean)

    types_credit=relationship("Types_credit")
    borrower = relationship("Borrower")

class Types_credit(Base):
    __tablename__='types_credit'
    idType = Column(Integer, primary_key=True)
    name = Column(String(45))
    condition = Column(String(45), nullable=True)
    rate = Column(Integer)
    term = Column(Date)

class Repayment(Base):
    __tablename__='repayment'
    idRepayment=Column(Integer, primary_key=True)
    idCredit = Column(Integer, ForeignKey('credit.idCredit'))
    soum = Column(Integer)
    date = Column(Date)

    credit = relationship("Credit")

class Borrower(Base):
    __tablename__='borrower'
    idBorrower = Column(Integer, primary_key=True)
    name = Column(String(45))
    address = Column(String(45))
    tel_num = Column(String(45))
    property = Column(String(45))
    confidant = Column(String(45))

