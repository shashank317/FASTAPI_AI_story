import sqlite3
import sys

print(f"Python version: {sys.version}")
print(f"SQLite library version: {sqlite3.sqlite_version}")

if sqlite3.sqlite_version_info >= (3, 9, 0):
    print("Your SQLite version has native JSON support. Great!")
else:
    print("Your SQLite version does not have native JSON support. SQLAlchemy will use TEXT as a fallback.")

