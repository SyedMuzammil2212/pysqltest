# from db.session import Base
# import models

# print(Base.metadata.tables.keys())



# from cores.security import hash_password
# print(hash_password("Superman@10"))


from cores.security import hash_password

hashed = hash_password("Superman@10")
print(hashed)