"""

"""
# ---
import sys
import os
import os.path as P
import traceback

# ---
import time
import datetime as DT
import glob

# ---
import settings as S
import database as DB

# ---
def get_icons():
    path = S.PATH_IMAGES
    mask = P.join(path, '*.png')
    result = glob.glob(mask)
    icons = []
    for icon in result:
        icon = P.split(icon)[1]
        icons.append(icon)
    return icons

def do(db_function):
    db = DB.DB()
    db.connect()
    result = db_function(db)()
    db.disconnect()
    return result

def get_users(db):
    # return the name of the function
    return db.get_users

def get_parties(db):
    # return the name of the function
    return db.get_parties