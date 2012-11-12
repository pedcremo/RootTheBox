'''
Created on Nov 11, 2012

@author: moloch

    Copyright 2012 Root the Box

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
'''


import json
import pylibmc
import logging

from uuid import uuid4
from models import dbsession, Snapshot, SnapshotTeam, Team
from sqlalchemy import func 
from libs.Singleton import Singleton


@Singleton
class GameHistory():
    '''
    List-like object to store game history, with cache to avoid
    multiple large database reads.
    '''

    def __init__(self):
        self.cache = pylibmc.Client(['127.0.0.1'], binary=True)
        self.__load__()

    def __load__(self):
        ''' Moves snapshots from db into the cache '''
        logging.debug("Loading game history from database ...")
        if 0 == len(Snapshot.all()):
            self.__now__() # Take initial snapshot
        for snapshot in Snapshot.all():
            if not snapshot.key in self.cache:
                logging.debug("Loaded snapshot taken on %s." % str(snapshot.created))
                self.cache.set(snapshot.key, snapshot.to_json())

    def take_snapshot(self):
        ''' Take a snapshot of the current game data '''
        logging.debug("Taking game data snapshot.")
        snapshot = self.__now__()
        self.cache.set(snapshot.key, snapshot.to_json())
        return snapshot
    
    def __now__(self):
        ''' Returns snapshot object it as a dict '''
        snapshot = Snapshot()
        for team in Team.all():
            snapshot_team = SnapshotTeam(
                team_id=team.id,
                money=team.money,
            )
            snapshot_team.game_levels = team.game_levels
            snapshot_team.flags = team.flags
            dbsession.add(snapshot_team)
            dbsession.flush()
            snapshot.teams.append(snapshot_team)
        dbsession.add(snapshot)
        dbsession.flush()
        return snapshot

    def __len__(self):
        return dbsession.query(func.max(Snapshot.id)) 

    def __getitem__(self, key):
        if isinstance(key, slice):
            return [self[index] for index in xrange(*key.indices(len(self)))]
        elif isinstance(key, int):
            if key < 0: # Handle negative indices
                key += len(self)
            if key >= len(self):
                raise IndexError("The index (%d) is out of range." % key)
            return self.__at__(key)
        else:
            raise TypeError("Invalid index argument to GameHistory")

    def __at__(self, index):
        ''' Get snapshot at specific index '''
        if Snapshot.to_key(index) in self.cache:
            return self.cache.get(key)
        else:
            snapshot = Snapshot.by_id(key)
            self.cache.set(snapshot.key, snapshot.game_data)
            return snapshot