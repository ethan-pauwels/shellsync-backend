from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()

# Enum for boat status
class BoatStatus(enum.Enum):
    available = "available"
    reserved = "reserved"
    maintenance = "maintenance"

# Boathouse model
class Boathouse(Base):
    __tablename__ = "boathouses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    contact_email = Column(String, nullable=False)
    location = Column(String)

    users = relationship("User", back_populates="boathouse")
    boats = relationship("Boat", back_populates="boathouse")
    reservations = relationship("Reservation", back_populates="boathouse")

# User model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="rower")  # 'rower' or 'admin'
    boathouse_id = Column(Integer, ForeignKey("boathouses.id"))

    boathouse = relationship("Boathouse", back_populates="users")
    reservations = relationship("Reservation", back_populates="user")

# Boat model
class Boat(Base):
    __tablename__ = "boats"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # e.g., "single", "double", "quad"
    status = Column(Enum(BoatStatus), default=BoatStatus.available)
    boathouse_id = Column(Integer, ForeignKey("boathouses.id"))

    boathouse = relationship("Boathouse", back_populates="boats")
    reservations = relationship("Reservation", back_populates="boat")

# Reservation model
class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    boat_id = Column(Integer, ForeignKey("boats.id"))
    boathouse_id = Column(Integer, ForeignKey("boathouses.id"))
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    status = Column(String, default="confirmed")  # could also use Enum

    user = relationship("User", back_populates="reservations")
    boat = relationship("Boat", back_populates="reservations")
    boathouse = relationship("Boathouse", back_populates="reservations")
