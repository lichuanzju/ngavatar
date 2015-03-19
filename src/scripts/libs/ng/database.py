"""This module defines low level API for accessing databases."""


import abc
import MySQLdb
from excepts import NGError
from excepts import HttpError


class DatabaseAccessError(HttpError):
    """Error that is raised when failed to access database."""

    def __init__(self, reason):
        """Create database access error with specified reason."""
        HttpError.__init__(self, 500)
        self.reason = str(reason)

    def __str__(self):
        """Return description of this error."""
        return 'Database access error - %s' % self.reason


class DatabaseIntegerityError(NGError):
    """Error that is raised when failed to execute operations in Database
    because of data integerity constraints such as UNIQUE keys."""

    def __init__(self, reason):
        """Create database integerity error with specified reason."""
        self.reason = str(reason)

    def __str__(self):
        """Return description of this error."""
        return 'Database integerity error - %s' % self.reason


class Database(object):
    """Abstract class that defines the API of databases."""

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_query_result(self, query_sql, args=None):
        """Abstract method that executes a sql query in the database and
        return the result as nested tuples. args is a sequence or dictionary
        used to format the query_sql string."""
        pass

    @abc.abstractmethod
    def execute_sql(self, sql, args=None, commit=True):
        """Abstract method that executes a sql statement (INSERT/UPDATE/
        DELETE). args is used to format the sql string. commit is a boolean
        value that indicates whether commit after execution is required."""
        pass

    @abc.abstractmethod
    def commit_transaction(self):
        """Abstract method that commits the current transaction."""
        pass

    @abc.abstractmethod
    def close(self):
        """Abstract method that closes the database connection."""
        pass

    def __enter__(self):
        """Method that is called when entering context."""
        return self

    def __exit__(self,
                 exception_type, exception_value, exception_traceback):
        """Method that is called when exiting context."""
        self.close()
        return False


class MySQLDatabase(Database):
    """Database that connects to MySQL."""

    def __init__(self, connect_params):
        """Create a MySQL database with connection parameters."""
        if connect_params is None:
            self.connect_params = {}
        else:
            self.connect_params = connect_params
        self.db = self._open_connection()
        self.cursor = self.db.cursor()

    def _open_connection(self):
        """Open connection to database and return the connection object"""
        try:
            return MySQLdb.connect(**self.connect_params)
        except MySQLdb.MySQLError as e:
            raise DatabaseAccessError(e)

    def get_query_result(self, query_sql, args=None):
        """Execute a query statement in MySQL database and return the
        result as nested tuples. args is used to format the query_sql
        string."""
        try:
            self.cursor.execute(query_sql, args)
            return self.cursor.fetchall()
        except MySQLdb.MySQLError as e:
            raise DatabaseAccessError(e)

    def execute_sql(self, sql, args=None, commit=True):
        """Execute a sql statement in MySQL database and return number
        of affected rows. args is used to format the sql string. commit
        indicates whether a commit operation is required after execution."""
        try:
            rows = self.cursor.execute(sql, args)
            if commit:
                self.db.commit()
            return rows
        except MySQLdb.MySQLError as e:
            self.db.rollback()
            if isinstance(e, MySQLdb.IntegrityError):
                raise DatabaseIntegerityError(e)
            else:
                raise DatabaseAccessError(e)

    def commit_transaction(self):
        """Commit the current transaction."""
        try:
            self.db.commit()
        except Exception as e:
            raise DatabaseAccessError(e)

    def close(self):
        """Close connection to MySQL database."""
        try:
            self.db.close()
        except Exception as e:
            raise DatabaseAccessError(e)
