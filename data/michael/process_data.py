# imports ######################################################################

# sqlalchemy related
from sqlalchemy import create_engine, MetaData, Column, Integer, String, Float, ARRAY, Table
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base

# standard
import sys, os, bz2, json

# utility
import pandas as pd
import numpy as np

# classes ######################################################################

Base = declarative_base()

# NC county class which serves
#     as an anchor points for our Tables.
class NCCounty(Base):
    __tablename__ = 'NC Counties' # non-standard naming but w.e.
    id       = Column(Integer, primary_key=True)
    name     = Column(String(255))
    boundary = Column(ARRAY(Float))

    def in_boundary(self, point):
        """ determine whether a point is contained within the
             boundary associated with this county """
        crossings = 0
        for ii in range(0, len(self.boundary)-1):
            x1 = self.boundary[ii][0]
            x2 = self.boundary[ii+1][0]

            if (point[0] >= x1) and (point[0] >= x2):
                continue

            y1 = self.boundary[ii][1]
            y2 = self.boundary[ii+1][1]

            if y2 > y1:
                if (point[1] >= y1) and (point[1] < y2):
                    if (point[0] <= x1) and (point[0] <= x2):
                        crossings += 1
                        continue
                    

                    xref = x1 + (point[1] - y1)*(x2-x1)/(y2-y1)
                    if point[0] < xref:
                        crossings += 1
                        continue
                    pass
                pass
            elif y1 > y2:
                if (point[1] >= y2) and (point[1] < y1):
                    if (point[0] <= x1) and (point[0] <= x2):
                        crossings += 1
                        continue

                    xref = x1 + (point[1] - y1)*(x2-x1)/(y2-y1)
                    if point[0] < xref:
                        crossings += 1
                        continue
                    pass
                pass
            pass
        return ((crossings % 2) == 1)
    pass

# class describing the table containing 
#  county level lightening strike data
class LightningStrikes(Base):
    __tablename__ = 'CountyStrikes'
    id      = Column(Integer, primary_key=True)
    Lightning_Strikes = Column(Integer) # number of lightening strikes in county
    
    pass

# methods ######################################################################

def load_counties(session):
    """ Load list of counties """
    objs = session.query(NCCounty).all()
    return objs    

def load_data(path):
    """ Load data from bzip'd raw json """
    # will hold aggregated json
    objs = []

    # open and process contents of bzip'd json file
    #  combining all lines into a single list
    with bz2.open(path, 'r') as ifile:
        for line in ifile:
            if len(line) > 1:
                objs.extend(json.loads(line))

    # convert "POINT" entries into tubles and rename
    #  some attributes
    for obj in objs:
        s = obj.get('center_point').split(' ')
        obj['point'] = (float(s[0][6:]), float(s[1][:-1]))
        del obj['center_point']

        obj['strikes'] = obj['number_of_strikes']
        del obj['number_of_strikes']
        
    return objs

def main():
    # path to lightenting data
    datafile = './raw-lightning.json.bz2'
    
    # setup connection to postgresql database
    engine  = create_engine(
        "postgresql://postgres@localhost:5432/project3")
    conn    = engine.connect()
    session = Session(bind=engine)

    print(f'=> Loading county data')
    # extract counties from database
    counties = load_counties(session)

    print(f'=> Loading lightning strike data')
    # load data to be binned by county
    objs = load_data(datafile)

    # combine objects into a 2d-histogram

    global hist # for debuging
    hist = dict()

    print(f'=> Building historgram')
    for obj in objs:
        pt = obj.get('point')
        hist[pt]  = hist.get(pt, 0) + obj.get('strikes')
        
    # process the lightning strike records and
    #  bin them if they are recorded occuring within a particular county
    
    global results # for debuging
    results = dict()

    print(f'=> Bining results by county')
    for pt in hist:
        # if the point is somewhere close to NC,
        if (pt[0] < -75.0) and (pt[0] > -85.0) and \
           (pt[1] < 37.0) and (pt[1] > 33.0):
            # then see which county it might be in
            found = False
            for county in counties:
                if county.in_boundary(pt):
                    results[county.id] = results.get(county.id, 0) \
                        + hist[pt]
                    found = True
                    print('==>', county.name, pt)
                    break
                pass
            if found:
                hist[pt] = 1
            else:
                hist[pt] = 0.5   
        else:
            hist[pt] = 0
            pass
        pass

    # create table for insertion into database
    meta = MetaData()
    lightning_table = Table(
        LightningStrikes.__tablename__, meta,
        Column('id', Integer, primary_key=True),
        Column('Lightning_Strikes', Integer))
    meta.create_all(engine)
    
    # commit changes to server
    session.commit()

    for cid in results:
        obj = LightningStrikes(id=cid, Lightning_Strikes=results[cid])
        session.add(obj)
        session.commit()

    session.add(
        LightningStrikes(id=95, Lightning_Strikes=0))
    session.commit()
    return 

# script entry-point ###########################################################

if __name__=="__main__":
    main()      # do main task
    sys.exit(0) # exit cleanly
