import pandas as pd
from sqlalchemy import create_engine

df = pd.read_excel('C:/Users/살구/Desktop/AI활용 아이디어경진대회/program/data/merged_data.xlsx')

if 'Unnamed: 0' in df.columns:
    df = df.drop(columns=['Unnamed: 0'])

user = 'root'             
password = '15861'      
host = '127.0.0.1'           
port = 3306
db_name = 'job_recoder'      

engine = create_engine(
    f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}",
    connect_args={"charset": "utf8mb4"} 
)

df.to_sql(name='merged_trainee_data', con=engine, if_exists='replace', index=False)

print("✅ MariaDB 테이블에 데이터 업로드 완료!")
