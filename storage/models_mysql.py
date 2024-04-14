from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
#from sqlalchemy.orm import DeclarativeBase, mapped_column
from sqlalchemy import Integer, String, DateTime, func
import datetime

Base = declarative_base()
#class Base(DeclarativeBase):
#    pass

class TrafficFlow(Base):
    __tablename__ = 'traffic_report'

    id = Column(Integer, primary_key=True, autoincrement=True)
    trace_id = Column(String(150), nullable=False)
    traffic_id = Column(String(150), nullable=False)
    intersection_id = Column(String(50), nullable=False)
    dateRecorded = Column(String(150), nullable=False)
    vehicle_count = Column(Integer, nullable=False)
    date_created = Column(DateTime, nullable=False, default=func.now())

    # def __init__(self, trace_id, traffic_id, intersection_id, dateRecorded, vehicle_count):
    #     """ Initializes a blood pressure reading """
    #     self.trace_id = trace_id
    #     self.traffic_id = traffic_id
    #     self.intersectionId = intersection_id
    #     self.dateRecorded = dateRecorded
    #     self.vehicleCount = vehicle_count
    #     # self.date_created = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

    def to_dict(self):
        """ Dictionary Representation of a Traffic reading """
        dict = {}
        dict['id'] = self.id
        dict['trace_id'] = self.trace_id
        dict['traffic_id'] = self.traffic_id
        dict['intersectionId'] = self.intersection_id
        dict['dateRecorded'] = self.dateRecorded
        dict['vehicleCount'] = self.vehicle_count
        dict['date_created'] = self.date_created

        return dict

class IncidentReport(Base):
    __tablename__ = 'incident_report'

    id = Column(Integer, primary_key=True, autoincrement=True)
    trace_id = Column(String(150), nullable=False)
    accident_id = Column(String(50), nullable=False)
    camera_id = Column(String(50), nullable=False)
    timestamp = Column(String(150), nullable=False)
    incidentType = Column(String(150), nullable=False)
    date_created = Column(DateTime, nullable=False, default=func.now())


    def to_dict(self):
        """ Dictionary Representation of a Incident reading """
        dict = {}
        dict['id'] = self.id
        dict['trace_id'] = self.trace_id
        dict['accident_id'] = self.accident_id
        dict['cameraId'] = self.camera_id
        dict['timestamp'] = self.timestamp
        dict['incidentType'] = self.incidentType
        dict['date_created'] = self.date_created

        return dict
