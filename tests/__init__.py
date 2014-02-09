# -*- coding: utf-8 -*-
'''
Created on Mar 12, 2012

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

import os
import logging

from libs.ConfigManager import ConfigManager


def setup_database(db_name):
    # Setup the test database
    logging.debug("Setting up the test database connection ...")
    config_manager = ConfigManager.instance()
    config_manager.db_connection = 'sqlite:///%s.db' % db_name
    assert config_manager.db_connection == 'sqlite:///%s.db' % db_name

    # Create the default tables
    logging.debug("Creating tables ... ")
    from setup.create_database import create_tables, engine, metadata
    create_tables(engine, metadata, False)
    import setup.bootstrap


def teardown_database(db_name):
    if os.path.exists("%s.db" % db_name):
        os.unlink("%s.db" % db_name)