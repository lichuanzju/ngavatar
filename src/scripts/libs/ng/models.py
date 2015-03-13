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


class Avatar(DatabaseModel):
    """Avatar model."""

    _table_name = 'avatar'
    _cols = [
        'aid',
        'owner_uid',
        'file_path',
        'add_time'
    ]
    _pk_col_index = 0

    @classmethod
    def file_path_exists(cls, db, owner_account, file_path):
        """Check whether the avatar with file_path exists in database."""
        return Avatar.count_in_database(
            db,
            owner_uid=owner_account['uid'],
            file_path=file_path
        ) != 0

    @classmethod
    def create_avatar(cls, db, owner_account, file_path):
        """Create a new avatar in database."""
        # Get the adding time
        now = datetime.datetime.now()

        # Create the instance and insert it to database
        new_avatar = Avatar(
            owner_uid=owner_account['uid'],
            file_path=file_path,
            add_time=now
        )
        new_avatar.insert_to_database(db)

        # Reload the instance from database
        new_avatar.reload_from_database(db, 'owner_uid', 'file_path')

        return new_avatar


class Email(DatabaseModel):
    """Model that represents email addresses."""

    _table_name = 'email'
    _cols = [
        'emid',
        'email',
        'owner_uid',
        'email_hash',
        'state',
        'avatar_id',
        'add_time',
        'verification_code',
        'verification_expire_time'
    ]
    _pk_col_index = 0

    STATE_NOTVERIFIED = 0
    STATE_VERIFIED = 1

    @classmethod
    def email_exists(cls, db, email):
        """Check whether the email address already exists in database."""
        return Email.count_in_database(db, email=email) != 0

    @classmethod
    def email_expired(cls, db, email):
        """Check whether the email address is expired."""
        email_object = Email.load_from_database(db, email=email)
        now = datetime.datetime.now()
        return email_object['state'] == cls.STATE_NOTVERIFIED and \
            email_object['verification_expire_time'] < now

    @classmethod
    def create_email(cls, db, owner_account, email, effective_hours=24):
        """Create a new email address in database and return it."""
        # Generate hash and verification code
        email_hash = str_generator.sha1_hexdigest(email, 40)
        verification_code = str_generator.random_string(20)

        # Get time of adding and time for verification code to expire
        add_time = datetime.datetime.now()
        verification_expire_time = add_time + \
            datetime.timedelta(0, effective_hours * 3600)

        # Create new email instance and insert it to database
        new_email = Email(
            email=email,
            owner_uid=owner_account['uid'],
            email_hash=email_hash,
            state=cls.STATE_NOTVERIFIED,
            add_time=add_time,
            verification_code=verification_code,
            verification_expire_time=verification_expire_time
        )
        new_email.insert_to_database(db)

        # Reload the new instance from database
        new_email.reload_from_database(db, 'email')

        return new_email

    def renew_verification(self, db, effective_hours=24):
        """Renew the verification code."""
        # Generate new verification information
        verification_code = str_generator.random_string(20)
        now = datetime.datetime.now()
        expire_time = now + \
            datetime.timedelta(0, effective_hours * 3600)

        # Change attributes of this instance
        self['verification_code'] = verification_code
        self['verification_expire_time'] = expire_time

        # Update changed attributes to database
        self.update_to_database(db,
                                'verification_code',
                                'verification_expire_time') == 1

    def verify(self, db, verification_code):
        """Verify this email address. Returning 0 means verified
        successfully, 1 means this email has already been verified,
        2 means the verification is incorrect, 3 means verification
        code is expired, 4 means failed to access database."""
        # Check the current state
        if self['state'] != self.__class__.STATE_NOTVERIFIED:
            return 1

        # Check the verification code
        if verification_code != self['verification_code']:
            return 2

        # Check the expiring time
        now = datetime.datetime.now()
        if now > self['verification_expire_time']:
            return 3

        # Change the state
        self['state'] = self.__class__.STATE_VERIFIED

        # Update the state to database
        lines = self.update_to_database(db, 'state')
        if lines == 1:
            return 0
        else:
            return 4


class Session(DatabaseModel):
    """Model that stores the http session data."""

    _table_name = 'session'
    _cols = [
        'sid',
        'session_key',
        'data',
        'expire_time',
        'creator_ip'
    ]
    _pk_col_index = 0

    @classmethod
    def session_exists(cls, db, session_key):
        """Check whether the session already exists in database."""
        return cls.count_in_database(db,
                                     session_key=session_key) != 0

    @classmethod
    def create_session(cls, db, session_key, data,
                       creator_ip, effective_hours=72):
        """Create session instance in database."""
        # Get expire time
        now = datetime.datetime.now()
        expire_time = now + datetime.timedelta(0, effective_hours * 3600)

        # Create session instance and insert to database
        new_session = Session(
            session_key=session_key,
            data=data,
            expire_time=expire_time,
            creator_ip=creator_ip
        )
        new_session.insert_to_database(db)

        # Reload the instance from database
        new_session.reload_from_database(db, 'session_key')

        return new_session

    def renew_session(self, db, effective_hours=72):
        """Renew this session."""
        # Get expire time
        now = datetime.datetime.now()
        expire_time = now + datetime.timedelta(0, effective_hours * 3600)

        self['expire_time'] = expire_time

        return self.update_to_database(db, 'expire_time') == 1
