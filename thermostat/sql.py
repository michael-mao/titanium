# -*- coding: utf-8 -*-

import os
import csv
import sqlite3 as lite

from logging import getLogger
from . import utils


class DB:

    def __init__(self, db_name='app.db'):
        self.db_name = db_name
        path = os.path.abspath(os.path.join(utils.BASE_DIR, '..', self.db_name))
        self.conn = lite.connect(path)
        self.cursor = self.conn.cursor()
        self.cursor.executescript(
            '''
            CREATE TABLE IF NOT EXISTS
            cost_schedule(
                country_code VARCHAR(2) NOT NULL,
                city VARCHAR(50) NOT NULL,
                company VARCHAR(50),
                start_time INTEGER NOT NULL,
                cost VARCHAR(8),
                PRIMARY KEY(country_code, city, company, start_time, cost)
            );
            '''
        )
        self.logger = getLogger('app.db')
        self.logger.debug('connected to db')

    def __del__(self):
        self.close()

    def insert(self, row, commit=True):
        raise NotImplementedError

    def select(self, where):
        raise NotImplementedError

    def commit(self):
        self.conn.commit()
        self.logger.debug('committed changes')

    def close(self):
        self.conn.close()


class CostTable(DB):

    def __init__(self):
        super().__init__()

    def insert(self, row, commit=True):
        self.cursor.execute(
            "INSERT INTO cost_schedule VALUES (:country_code, :city, :company, :start_time, :cost)", row
        )
        self.logger.debug('inserted row: {0}'.format(row))
        if commit is True:
            self.commit()

    def insert_csv(self, filename, commit=True):
        with open(filename) as f:
            csv_data = csv.reader(f)
        for row in csv_data:
            self.cursor.execute("INSERT INTO cost_schedule VALUES (?)", row)
        if commit is True:
            self.commit()

    def select(self, where):
        self.cursor.execute(
            "SELECT * FROM cost_schedule WHERE country_code=:country_code AND city=:city AND company=:company", where
        )
        self.logger.debug('selecting rows where: {0}'.format(where))
        return self.cursor.fetchall()
