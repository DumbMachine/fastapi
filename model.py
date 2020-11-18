"""Modelling of the database for the following entitites:
- Event
    id: int
    title: string
    description: string
    image: BLOB
    date: date
    location: string
    allowed_attendees: int
    waitlist: int
    startTime: date
    endTime: date

- User
    id: int
    name: string
    email: string

- Assumptions:
    User can be associated with my events
"""
import os

from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, Date

# Global Variables
SQLITE = 'sqlite'

# Table Names
USERS = 'users'
EVENTS = 'events'


def get_db():
    db = AppDatabase(SQLITE, dbname="temp")
    db.create_db_tables()

    return db


basedir = os.path.abspath(os.path.dirname(__file__))

class AppDatabase:
    """Master Database for Event and User management for the assigment
    """
    DB_ENGINE = {
        SQLITE: "sqlite:///" + os.path.join(basedir, "app.db"),
    }

    # Main DB Connection Ref Obj
    db_engine = None

    def __init__(self, dbtype, username='', password='', dbname=''):
        dbtype = dbtype.lower()

        if dbtype in self.DB_ENGINE.keys():
            engine_url = self.DB_ENGINE[dbtype].format(DB=dbname)

            self.db_engine = create_engine(engine_url)
            print(self.db_engine)

        else:
            print("DBType is not found in DB_ENGINE")

    def commit(self):
        """Simpler interface for commiting the database, not really the best practise
        """
        with self.db_engine.connect() as connection:
            connection.connection.commit()

    def rollback(self):
        """Simpler interface for commiting the database, not really the best practise
        """
        with self.db_engine.connect() as connection:
            connection.connection.rollback()

    def create_db_tables(self):
        metadata = MetaData()

        self.events = Table(EVENTS, metadata,
                            Column('id', Integer, primary_key=True),
                            Column('title', String),
                            Column('description', String),
                            Column('image', String),
                            Column('eventDate', Date),
                            Column('location', String),
                            Column('allowedAttendees', Integer),
                            Column('waitlist', Integer),
                            Column('startTime', String),
                            Column('endTime', String)
                            )

        self.users = Table(USERS, metadata,
                           Column('id', Integer, primary_key=True),
                           Column('eid', String, ForeignKey('events.id')),
                           Column('name', String),
                           Column('email', String)
                           )

        try:
            metadata.create_all(self.db_engine)
            print("Tables created")
        except Exception as e:
            print("Error occurred during Table creation!")
            print(e)

    def print_all_data(self, table='', query=''):
        query = query if query != '' else "SELECT * FROM '{}';".format(table)
        print(query)

        with self.db_engine.connect() as connection:
            try:
                result = connection.execute(query)
            except Exception as e:
                print(e)
            else:
                for row in result:
                    print(row)  # print(row[0], row[1], row[2])
                result.close()

        print("\n")

    def insert_event(self, data, table=EVENTS):

        with self.db_engine.connect() as connection:
            query = f'''INSERT INTO events(
                id, title, description, eventDate, location,
                allowedAttendees, waitlist, startTime, endTime, image
                ) VALUES {tuple([i for i in list(data.values())])};'''

            result = connection.execute(query)

    def get_event(self, eid, table=EVENTS):

        with self.db_engine.connect() as connection:
            try:
                query = f'''SELECT * FROM events WHERE id={eid}'''
                result = connection.execute(query)
                return [row for row in result][0]
            except Exception as e:
                print(e)
                return "Event Not Found"

    def get_event_all(self,table=EVENTS):

        with self.db_engine.connect() as connection:
            try:
                query = f'''SELECT * FROM events'''
                result = connection.execute(query)
                return [row for row in result]
            except Exception as e:
                print(e)
                return "Event Not Found"

    def get_user_all(self, table=USERS):

        with self.db_engine.connect() as connection:
            try:
                query = f'''SELECT * FROM users'''
                result = connection.execute(query)
                return [row for row in result]
            except Exception as e:
                print(e)
                return "Event Not Found"

    def remove_event(self, eid, table=EVENTS):

        with self.db_engine.connect() as connection:
            try:
                event = self.get_event(eid)
                if event == "Event Not Found":
                    raise
                query = f'''DELETE FROM events WHERE id={eid}'''
                result = connection.execute(query)
                connection.connection.commit()
                return eid
            except Exception as e:
                print(e)
                return ("Event Not Found")


    def insert_user(self, data, table=EVENTS):

        with self.db_engine.connect() as connection:
            query = f'''INSERT INTO users(
                id, name, email
                ) VALUES {tuple([i for i in list(data.values())])};'''
            result = connection.execute(query)

            connection.connection.commit()

    def get_user(self, uid, table=EVENTS):

        with self.db_engine.connect() as connection:
            try:
                query = f'''SELECT * FROM users WHERE id={uid}'''
                result = connection.execute(query)
                return [row for row in result][0]
            except Exception as e:
                print(e)
                return "User Not Found"

    def remove_user(self, eid, table=USERS):

        with self.db_engine.connect() as connection:
            try:
                user = self.get_user(eid)
                if user == "User Not Found":
                    raise
                query = f'''DELETE FROM users WHERE id={eid}'''
                result = connection.execute(query)
                connection.connection.commit()
                return eid
            except Exception as e:
                print(e)
                return ("User Not Found")


    # # Examples

    # def sample_query(self):
    #     # Sample Query
    #     query = "SELECT first_name, last_name FROM {TBL_USR} WHERE " \
    #             "last_name LIKE 'M%';".format(TBL_USR=USERS)
    #     self.print_all_data(query=query)

    #     # Sample Query Joining
    #     query = "SELECT u.last_name as last_name, " \
    #             "a.email as email, a.address as address " \
    #             "FROM {TBL_USR} AS u " \
    #             "LEFT JOIN {TBL_ADDR} as a " \
    #             "WHERE u.id=a.user_id AND u.last_name LIKE 'M%';" \
    #         .format(TBL_USR=USERS, TBL_ADDR=EVENTS)
    #     self.print_all_data(query=query)

    # def sample_delete(self):
    #     # Delete Data by Id
    #     query = "DELETE FROM {} WHERE id=3".format(USERS)
    #     self.execute_query(query)
    #     self.print_all_data(USERS)

    #     # Delete All Data
    #     '''
    #     query = "DELETE FROM {}".format(USERS)
    #     self.execute_query(query)
    #     self.print_all_data(USERS)
    #     '''

    # def sample_insert(self):
    #     # Insert Data
    #     query = "INSERT INTO {}(id, first_name, last_name) " \
    #             "VALUES (3, 'Terrence','Jordan');".format(USERS)
    #     self.execute_query(query)
    #     self.print_all_data(USERS)

    # def sample_update(self):
    #     # Update Data
    #     query = "UPDATE {} set first_name='XXXX' WHERE id={id}"\
    #         .format(USERS, id=3)
    #     self.execute_query(query)
    #     self.print_all_data(USERS)
