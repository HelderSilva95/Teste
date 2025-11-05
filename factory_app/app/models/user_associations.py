"""
Tabelas de associação entre Users, Sectors e Machines
"""
from sqlalchemy import Column, Integer, ForeignKey, Table
from config.database import Base

# Associação Many-to-Many: User <-> Sector
user_sectors = Table(
    'user_sectors',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('sector_id', Integer, ForeignKey('sectors.id'), primary_key=True)
)

# Associação Many-to-Many: User <-> Machine
user_machines = Table(
    'user_machines',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('machine_id', Integer, ForeignKey('machines.id'), primary_key=True)
)
