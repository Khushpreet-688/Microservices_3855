from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime


class ClockIn(Base):
    """ Clock in """

    __tablename__ = "clock_in"

    id = Column(Integer, primary_key=True, autoincrement=True)
    trace_id = Column(String(100), nullable=False)
    emp_num = Column(String(20), nullable=False)
    emp_name = Column(String(250), nullable=False)
    store_code = Column(String(20), nullable=False)
    timestamp = Column(String(100), nullable=False)
    date_created = Column(DateTime, nullable=False)
    num_hours_scheduled = Column(Integer, nullable=False)
    late_arrival = Column(Integer, nullable=False)

    def __init__(self, trace_id, emp_num, emp_name, store_code, timestamp, num_hours_scheduled, late_arrival):
        """ Initializes a clock in record """
        self.trace_id = trace_id
        self.emp_num = emp_num
        self.emp_name = emp_name
        self.store_code = store_code
        self.timestamp = timestamp
        self.date_created = datetime.datetime.now() # Sets the date/time record is created
        self.num_hours_scheduled = num_hours_scheduled
        self.late_arrival = late_arrival

    def to_dict(self):
        """ Dictionary Representation of a clock in record """
        dict = {}
        dict['id'] = self.id
        dict['trace_id'] = self.trace_id
        dict['emp_num'] = self.emp_num
        dict['emp_name'] = self.emp_name
        dict['store_code'] = self.store_code
        dict['num_hours_scheduled'] = self.num_hours_scheduled
        dict['late_arrival'] = self.late_arrival
        dict['timestamp'] = self.timestamp
        dict['date_created'] = self.date_created

        return dict
