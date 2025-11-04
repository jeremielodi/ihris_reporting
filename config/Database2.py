from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config.Database import  dbParams

 
DATABASE_URL = "mysql+pymysql://"+ dbParams['user'] +":"+ dbParams['passwd'] +"@"+ dbParams['host'] +"/"+dbParams['database']

db_engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)

Base = declarative_base()


 