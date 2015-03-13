"""This module defines data models."""

import abc
import datetime
from database import Database
from excepts import HttpError
import str_generator


class ModelError(HttpError):
    """Error that is raised when failed to process models."""

    def __init__(self, reason):
        """Create model error with reason of error."""
        HttpError.__init__(self, 500)
        self.reason = reason

    def __str__(self):
        """Return description of this error."""
        return 'Failed to process model: %s' % self.reason


class DatabaseModel(dict):
    """Abstract class that defines models stored in database."""

    __metaclass__ = abc.ABCMeta

    _table_name = ''        # Name of the table that stores this model
    _cols = []              # Column names of the table
    _pk_col_index = 0       # Index of the primary-key column

    @classmethod
    def table_name(cls):
        """Return name of the table that stores this model."""
        return cls._table_name

    @classmethod
    def table_columns(cls):
        """Return columns of the table."""
        return cls._cols

    @classmethod
    def _primary_key(cls):
        """Return the name of the primary-key of this model."""
        return cls._cols[cls._pk_col_index]

    @classmethod
    def _create_with_query_result(cls, result):
        """Create a new instance with query result of 'select *'."""
        return cls(zip(cls._cols, result))

    @classmethod
    def _get_database_query_result(cls, db, **kwargs):
        """Get query result from database. kwargs contains the
        attributes to query with."""
        # Create SELECT statement
        sql = 'SELECT * FROM %s' % cls._table_name
        args = []

        # Add WHERE statement
        added = False
        for key, value in kwargs.items():
            # Add conditions of WHERE statement
            if not added:
                sql += ' WHERE %s=%%s' % key
                added = True
            else:
                sql += ' AND %s=%%s' % key

            # Add arguments of WHERE statement
            args.append(value)

        return db.get_query_result(sql, args)

    @classmethod
    def load_from_database(cls, db, **kwargs):
        """Create an instance with data from database. kwargs contains
        the attributes to query with."""
        # Get query result from database
        query_result = cls._get_database_query_result(db, **kwargs)

        # If query result is no empty, create an instance and return
        # Otherwise return None
        if query_result:
            return cls._create_with_query_result(query_result[0])
        else:
            return None

    @classmethod
    def load_multiple_from_database(cls, db, **kwargs):
        """Create multiple instances with data from database and return
        them as a sequence. kwargs contains the attributes to query with."""
        # Get query result from database
        query_result = cls._get_database_query_result(db, **kwargs)

        # Create a instance for each result and return them as a sequence
        return [cls._create_with_query_result(res) for res in query_result]

    def _primary_key_value(self):
        """Return the value of the primary key of this instance."""
        return self[self.__class__._primary_key()]

    def insert_to_database(self, db):
        """Insert self to database."""
        # Create INSERT statement
        sql = 'INSERT INTO %s VALUES (' % self.__class__._table_name
        args = []

        # Add values
        formats = ['%s'] * len(self.__class__._cols)
        sql += ', '.join(formats)
        args.extend([self.get(col) for col in self.__class__._cols])

        # End values
        sql += ')'

        return db.execute_sql(sql, args)

    def reload_from_database(self, db, *query_cols):
        """Reload this instance from database using a query
        with specified columns. Primary key is used if no columns given"""
        # Use primary key to query if no column is given
        if not query_cols:
            query_cols.append(self.__class__._primary_key())

        # Collect attributes to query this instance with
        query_conditions = {}
        for col in query_cols:
            query_conditions[col] = self[col]

        # Find this instance in database
        query_result = self.__class__._get_database_query_result(
            db, **query_conditions)

        # Update value of this instance
        if len(query_result) == 0:
            raise ModelError('cannot find instance when reloading model')
        elif len(query_result) > 1:
            raise ModelError('mutiple instances found when reloading model')
        else:
            for key, value in zip(self.__class__._cols, query_result[0]):
                self[key] = value

    def delete_from_database(self, db):
        """Delete self from database."""
        # Create DELETE statement
        sql = 'DELETE FROM %s WHERE %s=%%s' % \
            (self.__class__._table_name, self.__class__._primary_key())
        args = [self._primary_key_value()]

        return db.execute_sql(sql, args)

    def store_to_database(self, db):
        """Store self to database by updating all attributes."""
        return self.update_to_database(db, self.__class__._cols)

    def update_to_database(self, db, *cols_to_update):
        """Update self in database.
        cols_to_update contains attributes to update."""
        # If no column needs to update, return 0
        if not cols_to_update:
            return 0L

        # Create UPDATE statement
        sql = 'UPDATE %s SET ' % self.__class__._table_name
        args = []

        # Add attributes to update
        updates = []
        for col in cols_to_update:
            updates.append('%s=%%s' % col)
            args.append(self.get(col))
        sql += ', '.join(updates)

        # Add WHERE statement
        sql += ' WHERE %s=%%s' % self.__class__._primary_key()
        args.append(self._primary_key_value())

        return db.execute_sql(sql, args)

    @classmethod
    def count_in_database(cls, db, **kwargs):
        """Return number of instances in database."""
        # Create SELECT statement
        sql = 'SELECT COUNT(*) FROM %s' % cls._table_name
        args = []

        # Add WHERE statement
        added = False
        for key, value in kwargs.items():
            # Add conditions of WHERE statement
            if not added:
                sql += ' WHERE %s=%%s' % key
                added = True
            else:
                sql += ' AND %s=%%s' % key

            # Add arguments of WHERE statement
            args.append(value)

        return db.get_query_result(sql, args)[0][0]


class Account(DatabaseModel):
    """User account model."""

    _table_name = 'account'
    _cols = [
        'uid',
        'username',
        'passwd_hash',
        'salt',
        'register_time',
        'login_time',
        'state',
    ]
    _pk_col_index = 0

    STATE_NORMAL = 0            # Normal state

    @classmethod
    def username_exists(cls, db, username):
        """Check where the username exists in the database."""
        return cls.count_in_database(db, username=username) != 0

    @classmethod
    def create_account(cls, db, username, password):
        """Create a new account in database and return it."""
        # Generate password hash
        salt = str_generator.random_string(5)
        password_hash = str_generator.sha1_hexdigest(
            password + salt,
            40
        )

        # Get account creating time
        now = datetime.datetime.now()

        # Create the account instance and write it to database
        new_account = Account(
            username=username,
            passwd_hash=password_hash,
            salt=salt,
            register_time=now,
            login_time=now,
            state=cls.STATE_NORMAL
        )
        new_account.insert_to_database(db)

        # Reload this instance from database
        new_account.reload_from_database(db, 'username')

        return new_account

    def check_password(self, password):
        """Check whether password is the correct for this account."""
        # Generate hash for this password
        password_hash = str_generator.sha1_hexdigest(
            password + self['salt'],
            40
        )

        # Compare the hash with the one in the database
        return password_hash == self['passwd_hash']

    def change_password(self, db, new_passwd):
        """Change password of this account."""
        # Generate hash for the new password
        salt = str_generator.random_string(5)
        password_hash = str_generator.sha1_hexdigest(
            new_passwd + salt,
            40
        )

        # Set the password to instance
        self['passwd_hash'] = password_hash
        self['salt'] = salt

        # Write the new password to database
        return self.update_to_database(db, 'passwd_hash', 'salt') == 1


class Profile(DatabaseModel):
    """User profile model."""

    _table_name = 'profile'
    _cols = [
        'pid',
        'owner_uid',
        'nickname',
        'sex',
    ]
    _pk_col_index = 0

    SEX_FEMALE = 0
    SEX_MALE = 1

    @classmethod
    def profile_exists(cls, db, owner_account):
        """Check whether the profile owned by owner_account exists
        in database."""
        return cls.count_in_database(db, owner_uid=owner_account['uid']) \
            != 0

    @classmethod
    def create_profile(cls, db, owner_account, nickname=None,
                       sex=None):
        """Create a new profile in database and return it."""
        # Use username as default nickname
        if not nickname:
            nickname = owner_account['username']

        # Set male as default sex
        if not sex:
            sex = cls.SEX_MALE

        # Create a new profile and store it to database
        new_profile = Profile(
            owner_uid=owner_account['uid'],
            nickname=nickname,
            sex=sex
        )
        new_profile.insert_to_database(db)

        # Reload this instance from database
        new_profile.reload_from_database(db, 'owner_uid')

        return new_profile

    def change_profile(self, db, nickname=None, sex=None):
        """Change attributes of the profile."""
        # Collect updated attributes
        updated_cols = []

        # Check nickname
        if nickname is not None:
            self['nickname'] = nickname
            updated_cols.append('nickname')

        # Check sex
        if sex is not None:
            self['sex'] = sex
            updated_cols.append('sex')

        # Update data in database
        return self.update_to_database(db, *updated_cols) == 1
