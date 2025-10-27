
from sqlalchemy import create_engine, text
import logging
import pandas as pd
# Name our logger so we know that logs from this module come from the data_ingestion module
logger = logging.getLogger('data_ingestion')
# Set a basic logging message up that prints out a timestamp, the name of our logger, and the message
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def create_db_engine(db_path):
    """
    Create a SQLAlchemy database engine and test the connection.

    Parameters
    ----------
    db_path : str
        The database connection string. For example:
        - "sqlite:///my_database.db" for SQLite
        - "postgresql://user:password@localhost/dbname" for PostgreSQL

    Returns
    -------
    engine : sqlalchemy.engine.Engine
        A SQLAlchemy Engine object that can be used to connect to the database.

    Raises
    ------
    ImportError
        If SQLAlchemy is not installed.
    Exception
        If the engine cannot be created or the connection test fails.

    Notes
    -----
    Uses a context manager (`with engine.connect()`) to ensure the test
    connection is opened and closed safely.
    """
    try:
        engine = create_engine(db_path)
        with engine.connect() as conn:
            pass
        logger.info("Database engine created successfully.")
        return engine
    except ImportError:
        logger.error("SQLAlchemy is required to use this function. Please install it first.")
        raise
    except Exception as e:
        logger.error(f"Failed to create database engine. Error: {e}")
        raise e


def query_data(engine, sql_query):
    """
    Execute an SQL query using a given SQLAlchemy engine and return the result as a DataFrame.

    Parameters
    ----------
    engine : sqlalchemy.engine.Engine
        A SQLAlchemy engine object connected to a database.
    sql_query : str
        The SQL query string to execute.

    Returns
    -------
    df : pandas.DataFrame
        DataFrame containing the query results.

    Raises
    ------
    ValueError
        If the query returns an empty result set.
    Exception
        If the query execution fails for any other reason.

    Notes
    -----
    Automatically closes the database connection using a context manager.
    """
    try:
        with engine.connect() as connection:
            df = pd.read_sql_query(text(sql_query), connection)
        if df.empty:
            msg = "The query returned an empty DataFrame."
            logger.error(msg)
            raise ValueError(msg)
        logger.info("Query executed successfully.")
        return df
    except ValueError as e:
        logger.error(f"SQL query failed. Error: {e}")
        raise e
    except Exception as e:
        logger.error(f"An error occurred while querying the database. Error: {e}")
        raise e


def read_from_web_CSV(URL):
    """
    Read a CSV file directly from a given web URL into a Pandas DataFrame.

    Parameters
    ----------
    URL : str
        The web URL pointing to a CSV file.

    Returns
    -------
    df : pandas.DataFrame
        DataFrame containing the contents of the CSV file.

    Raises
    ------
    pandas.errors.EmptyDataError
        If the URL does not point to a valid or non-empty CSV file.
    Exception
        If reading the CSV file fails for any other reason.

    Notes
    -----
    Useful for quickly ingesting CSV datasets hosted on the internet.
    """
    try:
        df = pd.read_csv(URL)
        logger.info("CSV file read successfully from the web.")
        return df
    except pd.errors.EmptyDataError as e:
        logger.error("The URL does not point to a valid CSV file. Please check the URL and try again.")
        raise e
    except Exception as e:
        logger.error(f"Failed to read CSV from the web. Error: {e}")
        raise e
