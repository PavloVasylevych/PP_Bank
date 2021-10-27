from tables import *

session=sessionmaker(bind=engine)

add_borrower1 = Borrower(idBorrower=1, name="Sergiy Gruber", address="Grétrystraat 63", tel_num="+43 01 5134505", property="three room flat", confidant="Eduardo Peeters")
add_borrower2 = Borrower(idBorrower=2, name="Kara Gonçalves", address="1498 rue Bélanger", tel_num="+49 0711 2842222", property="vacation home", confidant="Alex Philips")

add_types_credit = Types_credit(idType=1, name="Default", condition="none condition", rate=30, term='2021-10-26')

add_credit1 = Credit(idCredit=1, idType=1, idBorrower=1, soum=20000, date_of_issue='2020-10-10', canceled = True)
add_credit2 = Credit(idCredit=2, idType=1, idBorrower=2, soum=40000, date_of_issue='2021-10-15', canceled = False)

add_repayment1 = Repayment(idRepayment=1, idCredit= 1, soum=26000, date='2021-10-10')
add_repayment2 = Repayment(idRepayment=2, idCredit= 2, soum=30000, date='2021-10-27')
s=session()
s.add(add_borrower1)
s.add(add_borrower2)

s.add(add_types_credit)

s.add(add_credit1)
s.add(add_credit2)

s.add(add_repayment1)
s.add(add_repayment2)

s.commit()