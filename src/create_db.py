from database import create_tables, drop_tables
import sys

def main():
    """Create database tables"""
    print("Creating database tables...")

    try:
        # Uncomment the line below if you want to drop existing tables first
        # drop_tables()
        # print("Dropped existing tables")

        create_tables()
        print("Database tables created successfully!")

    except Exception as e:
        print(f"Error creating tables: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
