import os
import sys

# Add the project root directory (backend) to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.core.database import Base, engine
from app.models import user, portfolio, asset, transaction # Import all models

def main():
    print("Connecting to the database and creating tables...")
    try:
        # This command connects to the database and creates all tables
        # that inherit from the Base class.
        Base.metadata.create_all(bind=engine)
        print("Tables created successfully!")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
