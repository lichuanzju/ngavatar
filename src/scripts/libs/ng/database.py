"""This module defines low level API for accessing MySQL databases."""


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
        return the result as tuples."""
        pass

    @abc.abstractmethod
    def execute_sql(self, sql, args=None, commit=True):
        """Abstract method that executes a sql statement
        (INSERT/UPDATE/DELETE)."""
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
        return True


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
        """Open connection to the database."""
        try:
            return MySQLdb.connect(**self.connect_params)
        except MySQLdb.MySQLError as e:
            raise DatabaseAccessError(e)

    def get_query_result(self, query_sql, args=None):
        """Execute a query statement in MySQL database and return the
        result as tuples."""
        try:
            self.cursor.execute(query_sql, args)
            return self.cursor.fetchall()
        except MySQLdb.MySQLError as e:
            raise DatabaseAccessError(e)

    def execute_sql(self, sql, args=None, commit=True):
        """Execute a sql statement in MySQL database and return number
        of affected rows."""
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

    def __exit__(self,
                 exception_type, exception_value, exception_traceback):
        """Method that is called when exiting context."""
        self.close()
        return False


def test():
    connect_params = dict(host='localhost', port=3306,
                          user='lic', passwd='900124_li', db='test')

    print 'Inserting:'
    db = MySQLDatabase(connect_params)
    print db.execute_sql(
        'insert into test_table values (null, "lic2", "111")'
    )
    result = db.get_query_result('select * from test_table')
    db.close()
    print result

    print 'Deleting:'
    with MySQLDatabase(connect_params) as db:
        print db.execute_sql('delete from test_table where username=%s',
                             ['lic2'])
        result = db.get_query_result('select * from test_table')
        print result

    try:
        db.close()
        print 'Database not closed'
    except:
        print 'Database closed'


if __name__ == '__main__':
    test()
