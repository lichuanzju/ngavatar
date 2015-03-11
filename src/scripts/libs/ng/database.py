"""This module defines low level API for accessing MySQL databases."""


import abc
import MySQLdb
from excepts import HttpError


class DatabaseError(HttpError):
    """Error that is raised when failed to access database."""

    def __init__(self, reason):
        """Create database error with specified reason."""
        HttpError.__init__(self, 500)
        self.reason = reason

    def __str__(self):
        """Return description of this error."""
        return 'Failed to access database: %s' % self.reason


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
        self.connect_params = connect_params
        self.db = self._open_connection()
        self.cursor = self.db.cursor()

    def _open_connection(self):
        """Open connection to the database."""
        return MySQLdb.connect(**self.connect_params)

    def get_query_result(self, query_sql, args=None):
        """Execute a query statement in MySQL database and return the
        result as tuples."""
        self.cursor.execute(query_sql, args)
        return self.cursor.fetchall()

    def execute_sql(self, sql, args=None, commit=True):
        """Execute a sql statement in MySQL database and return number
        of affected rows."""
        try:
            rows = self.cursor.execute(sql, args)
            if commit:
                self.db.commit()
            return rows
        except Exception as e:
            self.db.rollback()
            raise DatabaseError(e)

    def commit_transaction(self):
        """Commit the current transaction."""
        try:
            self.db.commit()
        except Exception as e:
            raise DatabaseError(e)

    def close(self):
        """Close connection to MySQL database."""
        self.db.close()

    def __exit__(self,
                 exception_type, exception_value, exception_traceback):
        """Method that is called when exiting context."""
        self.close()

        # Pass DatabaseError instead of other errors
        if exception_type == DatabaseError:
            return False
        elif exception_type:
            raise DatabaseError(exception_value)


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
