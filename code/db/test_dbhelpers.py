import pytest
import db.dbhelpers as dbhelpers
import os
from unittest.mock import MagicMock, patch
import datetime


@pytest.fixture
def dbpath():
    try:
        os.remove('test.db')
    except:
        pass
    dbpath = 'test.db'
    dbhelpers.create_tables(db='test.db')
    yield dbpath
    os.remove(dbpath)


def test_get_flavour(dbpath):
    # Arrange
    expected = 'mage'
    conn, cursor = dbhelpers.connect(dbpath)
    query = """INSERT INTO players
               VALUES (10, 11, 12, 'mage', 'n/a')"""
    cursor.execute(query)
    conn.commit()
    cursor.close()
    conn.close()
    message = MagicMock()
    message.guild.id = 10
    message.channel.id = 11
    message.author.id = 12

    # Act
    actual = dbhelpers.get_flavour(message, dbpath)
    # Assert
    assert expected == actual


def test_get_flavour_default(dbpath):
    # Arrange
    expected = None
    conn, cursor = dbhelpers.connect(dbpath)
    query = """INSERT INTO players (server, channel, player)
                   VALUES (10, 11, 12)"""
    cursor.execute(query)
    conn.commit()
    cursor.close()
    conn.close()
    message = MagicMock()
    message.guild.id = 10
    message.channel.id = 11
    message.author.id = 12

    # Act
    actual = dbhelpers.get_flavour(message, dbpath)
    # Assert
    assert expected == actual


@patch('db.dbhelpers.datetime')
def test_get_flavour_update_last_roll(mock_datetime, dbpath):
    # Arrange
    #  Insert data to fake db
    conn, cursor = dbhelpers.connect(dbpath)
    query = """INSERT INTO players (server, channel, player, last_roll)
                       VALUES (10, 11, 12, '2020-04-01 12:34:56')"""
    cursor.execute(query)
    conn.commit()
    cursor.close()
    conn.close()

    #  Create mock for datetime.datetine.now()
    expected = '2020-05-01 00:00:00'
    fake_now_dt = datetime.datetime.strptime(expected, '%Y-%m-%d %H:%M:%S')
    mock_datetime.datetime.now.return_value = fake_now_dt

    #  Creat message mock
    message = MagicMock()
    message.guild.id = 10
    message.channel.id = 11
    message.author.id = 12

    # Act
    dbhelpers.get_flavour(message, dbpath)

    # Assert
    #  Get new values
    conn, cursor = dbhelpers.connect(dbpath)
    query = """SELECT last_roll FROM players"""
    cursor.execute(query)
    output = cursor.fetchone()
    actual = output[0]
    cursor.close()
    conn.close()

    assert expected == actual

@patch('db.dbhelpers.datetime')
def test_clear_inactive_records(mock_datetime, dbpath):
    # Arrange
    expected = [
        (10, 11, 13, None, '2020-05-30 12:34:56'),
        (10, 11, 14, None, '2020-05-01 12:34:56'),
    ]
    #  Insert fake data
    conn, cursor = dbhelpers.connect(dbpath)
    queries = [
        """INSERT INTO players (server, channel, player, last_roll)
                           VALUES (10, 11, 12, '2020-04-01 12:34:56');""",
        """INSERT INTO players (server, channel, player, last_roll)
                           VALUES (10, 11, 13, '2020-05-30 12:34:56');""",
        """INSERT INTO players (server, channel, player, last_roll)
                           VALUES (10, 11, 14, '2020-05-01 12:34:56');"""]
    for query in queries:
        cursor.execute(query)
    conn.commit()
    cursor.close()
    conn.close()

    #  Create mock for datetime.datetime.now()
    fake_now = '2020-05-31 00:00:00'
    fake_now_dt = datetime.datetime.strptime(fake_now, '%Y-%m-%d %H:%M:%S')
    mock_datetime.datetime.now.return_value = fake_now_dt

    #  Link mock_datetime.timedelta to proper timedelta function
    mock_datetime.timedelta = datetime.timedelta

    # Act
    dbhelpers.clear_inactive_records(dbpath)

    # Assert
    #  Get new values
    conn, cursor = dbhelpers.connect(dbpath)
    query = """SELECT * FROM players"""
    cursor.execute(query)
    actual = cursor.fetchall()
    cursor.close()
    conn.close()

    assert len(expected) == len(actual)
    assert expected == actual
