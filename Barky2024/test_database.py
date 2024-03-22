# the database module is much more testable as its actions are largely atomic
# that said, the database module could certain be refactored to achieve decoupling
# in fact, either the implementation of the Unit of Work or just changing to sqlalchemy would be good.

# I added a test for delete and made sure things were commented.  I did not create any tests for the commands 
# becuase this module is drawing on that heavily.
import os
from datetime import datetime, timezone
import sqlite3

import pytest


from database import DatabaseManager

@pytest.fixture
def database_manager() -> DatabaseManager:
    """
    A pytest fixture to set up a DatabaseManager instance for testing.

    What is a fixture? https://docs.pytest.org/en/stable/fixture.html#what-fixtures-are
    """
    filename = "test_bookmarks.db"
    dbm = DatabaseManager(filename)
    # what is yield? https://www.guru99.com/python-yield-return-generator.html
    yield dbm
    dbm.__del__()           # explicitly release the database manager
    os.remove(filename)


def test_database_manager_create_table(database_manager):
    """
    Test case to verify the creation of a table by the DatabaseManager.
    """
    # arrange and act
    database_manager.create_table(
        "bookmarks",
        {
            "id": "integer primary key autoincrement",
            "title": "text not null",
            "url": "text not null",
            "notes": "text",
            "date_added": "text not null",
        },
    )

    #assert
    conn = database_manager.connection
    cursor = conn.cursor()
    cursor.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='bookmarks' ''')
    assert cursor.fetchone()[0] == 1

    #cleanup
    # this is probably not really needed but it tests the drop function
    database_manager.drop_table("bookmarks")


def test_database_manager_add_bookmark(database_manager):
    """
    Test case to verify adding a bookmark to the database.
    """
    # arrange
    database_manager.create_table(
        "bookmarks",
        {
            "id": "integer primary key autoincrement",
            "title": "text not null",
            "url": "text not null",
            "notes": "text",
            "date_added": "text not null",
        },
    )

    data = {
        "title": "test_title",
        "url": "http://example.com",
        "notes": "test notes",
        "date_added": datetime.now(timezone.utc).isoformat()        
    }

    # act
    database_manager.add("bookmarks", data)
    # assert
    conn = database_manager.connection
    cursor = conn.cursor()
    cursor.execute(''' SELECT * FROM bookmarks WHERE title='test_title' ''')    
    assert cursor.fetchone()[0] == 1    

# I Added this test
    
def test_database_manager_delete_bookmark(database_manager):

    # arrange
    database_manager.create_table(
        "bookmarks",
        {
            "id": "integer primary key autoincrement",
            "title": "text not null",
            "url": "text not null",
            "notes": "text",
            "date_added": "text not null",
        },
    )

    data = {
        "title": "test_title",
        "url": "http://example.com",
        "notes": "test notes",
        "date_added": datetime.now(timezone.utc).isoformat()        
    }

    database_manager.add("bookmarks", data)
    
    #act
    database_manager.delete("bookmarks", {"title": "test_title"})
    
    # assert
    conn = database_manager.connection
    cursor = conn.cursor()
    cursor.execute(''' SELECT * FROM bookmarks WHERE title='test_title' ''')    
    result = cursor.fetchone()
    assert result is None or result[0] == 0