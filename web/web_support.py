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

def get_users():
    db = DB.DB()
    db.connect()
    users = db.get_users()
    db.disconnect()
    return users