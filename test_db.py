from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "mysql+pymysql://root:@localhost:3306/jobmatcher"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

try:
    db = SessionLocal()
    result = db.execute(text("SELECT 1")).fetchall()  # ✅ wrap query in text()
    print("✅ Database connection successful!", result)
except Exception as e:
    print("❌ Database connection failed:", e)
finally:
    db.close()
