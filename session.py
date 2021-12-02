from tables import *

session=sessionmaker(bind=engine)

s = session()

# add_user1 = User(id=1, username="SergiyGruber", password = "12345678", ClientName="Sergiy Gruber", firstName="Sergiy", lastName="Gruber", status="manager")
# add_user2 = User(id=2, username="GruberSergiy", password = "87654321", ClientName="Gruber Sergiy", firstName="Gruber", lastName="Sergiy", status="borrower")
#
# add_credit1 = Credit(id=1, id_borrower=2, loan_status=0, loan_date='2020-10-10', loan_amount=150000, interest_rate = 30)
#
# add_bank1 = Bank(bank_id=1,balance=570000)
# s=session()
# s.add(add_user1)
# s.add(add_user2)
#
# s.add(add_bank1)
#
# s.add(add_credit1)
#
#
# s.commit()