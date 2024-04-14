#from sqlalchemy.orm import DeclarativeBase, mapped_column
from sqlalchemy import Integer, String, DateTime, func, Column
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
#class Base(DeclarativeBase):
#    pass

class Stats(Base):
    __tablename__ = 'stats'

    id = Column(Integer, primary_key=True)
    num_traffic_report = Column(Integer, nullable=False)
    num_incident_report = Column(Integer, nullable=False)
    max_vehicle_count = Column(Integer, nullable=False)
    last_updated = Column(DateTime, nullable=False, default=func.now())


    def to_dict(self):
        """ Dictionary Representation of statics reading """
        dict = {}
        dict['id'] = self.id
        dict['num_traffic_report'] = self.num_traffic_report
        dict['num_incident_report'] = self.num_incident_report
        dict['max_vehicle_count'] = self.max_vehicle_count
        dict['last_updated'] = self.last_updated.strftime("%Y-%m-%dT%H:%M:%S.%f")
            
        return dict
