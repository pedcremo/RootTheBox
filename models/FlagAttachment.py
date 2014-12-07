# -*- coding: utf-8 -*-
'''
Created on Nov 24, 2014

@author: moloch

    Copyright 2014 Root the Box

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

import os

from uuid import uuid4
from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import Unicode, String, Integer
from models.BaseModels import DatabaseObject
from tornado.options import options


class FlagAttachment(DatabaseObject):

    '''
    These are files that the administrator wants to
    distribute alongside a flag.
    '''

    DIR = 'flag_attachments/'

    uuid = Column(String(36),
                  unique=True,
                  nullable=False,
                  default=lambda: str(uuid4())
                  )

    flag_id = Column(Integer, ForeignKey('flag.id'), nullable=False)
    _file_name = Column(Unicode(64), nullable=False)

    @property
    def file_name(self):
        return self._file_name

    @file_name.setter
    def file_name(self, value):
        fname = value.replace('\n', '').replace('\r', '')
        self._file_name = unicode(os.path.basename(fname))[:64]

    @property
    def data(self):
        config = ConfigManager.instance()
        with open(config.file_uploads_dir + self.DIR + self.uuid, 'rb') as fp:
            return fp.read().decode('base64')

    @data.setter
    def data(self, value):
        config = ConfigManager.instance()
        if self.uuid is None:
            self.uuid = str(uuid4())
        self.byte_size = len(value)
        with open(config.file_uploads_dir + self.DIR + self.uuid, 'wb') as fp:
            fp.write(value.encode('base64'))

    def delete_data(self):
        ''' Remove the file from the file system, if it exists '''
        config = ConfigManager.instance()
        fpath = config.file_uploads_dir + self.DIR + self.uuid
        if os.path.exists(fpath) and os.path.isfile(fpath):
            os.unlink(fpath)