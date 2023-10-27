from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime


class ClockOut(Base):
    """ Clock out """

    __tablename__ = "clock_out"

    id = Column(Integer, primary_key=True, autoincrement=True)
    trace_id = Column(String(100), nullable=False)
    emp_num = Column(String(20), primary_key=True)
    emp_name = Column(String(250), nullable=False)
    store_code = Column(String(20), nullable=False)
    timestamp = Column(String(100), nullable=False)
    date_created = Column(DateTime, nullable=False)
    num_hours_worked = Column(Integer, nullable=False)
    overtime_hours = Column(Integer, nullable=False)

    def __init__(self, trace_id, emp_num, emp_name, store_code, timestamp, num_hours_worked, overtime_hours):
        """ Initializes a clock out record """
        self.trace_id = trace_id
        self.emp_num = emp_num
        self.emp_name = emp_name
        self.store_code = store_code
        self.timestamp = timestamp
        self.date_created = datetime.datetime.now() # Sets the date/time record is created
        self.num_hours_worked = num_hours_worked
        self.overtime_hours = overtime_hours

    def to_dict(self):
        """ Dictionary Representation of a clock out record """
        dict = {}
        dict['id'] = self.id
        dict['trace_id'] = self.trace_id
        dict['emp_num'] = self.emp_num
        dict['emp_name'] = self.emp_name
        dict['store_code'] = self.store_code
        dict['num_hours_worked'] = self.num_hours_worked
        dict['overtime_hours'] = self.overtime_hours
        dict['timestamp'] = self.timestamp
        dict['date_created'] = self.date_created

        return dict