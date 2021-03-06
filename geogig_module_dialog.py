# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GeoGigDialog
                                 A QGIS plugin
 This plugin simplifies the GeoGig workflow .
                             -------------------
        begin                : 2015-03-18
        git sha              : $Format:%H$
        copyright            : (C) 2015 by Roscoe Lawrence
        email                : roscoelawrence@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import os
import geo_repo
from PyQt4 import QtGui, uic
import csv
import sys
import shutil




FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'geogig_module_dialog_base.ui'))


class GeoGigDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(GeoGigDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.configPath = os.path.dirname(os.path.realpath(__file__))
        self.fname = os.path.join(self.configPath, "config.csv")
        self.repo_dict = {}
        self.repo_type = "remote"
        self.export_type = "shapefiles"
        self.remote = ""
        self.path = ""
        self.key_no = 0
        #  self.sync_button.clicked.connect(self.clone_repo)

        self.get_fields()
        self.reload()
        self.radioRemote.toggled.connect(self.set_repo_type)
        # self.radioShapefilesClone.toggled.connect(self.set_repo_type)
        self.btnClone.clicked.connect(self.clone_repo)
        # self.btnSync.clicked.connect(self.sync_repo)
        self.btnAdd.clicked.connect(self.set_fields)
        self.btnDelete.clicked.connect(self.delete_field)
        self.btnPush.clicked.connect(self.push)
        self.listRepos.itemClicked.connect(self.set_repo_type)
        self.lblRepoStatus.setText('Not Connected')

    # Change set_repo_type to set_repo
    def set_repo_type(self):
        self.key_no = self.listRepos.row(self.listRepos.currentItem())
        if self.radioLocal.isChecked():
            self.repo_type = "local"
            self.txtRemote.setEnabled(False)

        else:
            self.repo_type = "remote"
            self.txtRemote.setEnabled(True)
        self.remote = self.repo_dict.keys()[self.key_no]
        self.path = self.repo_dict.values()[self.key_no]
        # self.remote = self.repo_dict.keys()[self.key_no]
        # self.path = self.repo_dict.values()[self.key_no]
        print self.repo_type
        print self.path
        print self.export_type
        print "remote: " + self.remote
        print "path: " + self.path

    def clone_repo(self):
        sql_database = os.path.join(self.path, 'database.sqlite')
        repos = geo_repo.GeoRepo(self.remote, self.path, self.repo_type)
        repos.export_to_shapefiles()

    def sync_repo(self):
        sql_database = self.path + 'database.sqlite'

        name = self.txtName.text()
        email = self.txtEmail.text()
        message = self.txtMessage.text()
        repos = geo_repo.GeoRepo(self.remote, self.path, self.repo_type)
        repos.add_commit_push(name, email, message)

    def get_fields(self):
        if os.path.isfile(self.fname):
            with open(self.fname, 'r+b') as csvfile_in:
                reader = csv.reader(csvfile_in)
                self.repo_dict = dict(row[:2] for row in reader if row)

        else:
            with open(self.fname, 'w+b') as csvfile:
                fieldnames = ['url', 'dir']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writerow({'url': 'Baked', 'dir': 'Beans'})

    def set_fields(self):
        new_repo = self.txtRemote.text()
        new_dir = self.txtDir.text()
        self.repo_dict.update({new_repo: new_dir})
        #self.repo_dict[new_repo] = [new_dir]
        self.save()
        self.reload()

    def save(self):
        with open(self.fname, 'w+b') as csvfile:
            writer = csv.writer(csvfile)
            for key, value in self.repo_dict.items():
                writer.writerow([key, value])

    def reload(self):
        self.listRepos.clear()
        self.repo_dict = {}
        self.get_fields()
        for item in self.repo_dict:
            self.listRepos.addItem(item + " : " + self.repo_dict[item])

    def delete_field(self):
        item = self.listRepos.currentItem().text()
        self.key_no = self.listRepos.row(self.listRepos.currentItem())
        key = self.repo_dict.keys()[self.key_no]
        value = self.repo_dict.values()[self.key_no]
        del self.repo_dict[key]
        shutil.rmtree(self.path, ignore_errors=True)
        self.save()
        self.reload()

    def push(self):
        repos = geo_repo.GeoRepo(self.remote, self.path, self.repo_type)
        print "Remote: " +self.remote + " Path: " + self.path
        repos.push_to_remote()

    def pull(self):
        repos = geo_repo.GeoRepo(self.remote, self.path, self.repo_type)
        repos.pull_from_remote()
        repos.export_to_shapefiles()

    def set_layers(self, list_layers):
        for layer in list_layers:
            if layer:
                self.listWidget.addItem(layer)
        






