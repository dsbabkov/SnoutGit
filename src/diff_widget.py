# -*- coding: utf-8 -*-
__author__ = 'panter.dsd@gmail.com'

from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot, QRegExp
from PyQt5.QtGui import QTextCursor, QTextOption
from PyQt5.QtWidgets import QSizePolicy

import commit
import git
import diff_highlighter


class DiffWidget(QtWidgets.QWidget):
    _id = str()
    _git = git.Git()

    def __init__(self, path, parent=None):
        super(DiffWidget, self).__init__(parent)

        self._path = path

        self._diff_view = QtWidgets.QPlainTextEdit(self)
        self._diff_view.setReadOnly(True)
        self._diff_view.setWordWrapMode(QTextOption.NoWrap)
        self._diff_view.setUndoRedoEnabled(False)
        self._highlighter = diff_highlighter.DiffHighlighter(
            self._diff_view.document())

        self._files_list = QtWidgets.QListWidget(self)
        self._files_list.itemPressed.connect(self._select_file)

        panel = QtWidgets.QWidget(self)
        panel.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        self._diff_lines_count_edit = QtWidgets.QSpinBox(self)
        self._diff_lines_count_edit.valueChanged.connect(self._update_diff)
        self._diff_lines_count_edit.setValue(3)

        panelLayout = QtWidgets.QHBoxLayout()
        panelLayout.addWidget(QtWidgets.QLabel("Context strings count"))
        panelLayout.addWidget(self._diff_lines_count_edit)

        spacer = QtWidgets.QSpacerItem(
            0, 0, QSizePolicy.Expanding, QSizePolicy.Preferred
        )

        panelLayout.addSpacerItem(spacer)

        panel.setLayout(panelLayout)

        horizontal_split = QtWidgets.QSplitter(self)
        horizontal_split.addWidget(self._diff_view)
        horizontal_split.addWidget(self._files_list)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(panel)
        layout.addWidget(horizontal_split)
        super(DiffWidget, self).setLayout(layout)

    @pyqtSlot(str)
    def set_commit(self, id):
        self._id = id
        self._update_diff()

    def _update_diff(self):
        current_commit = commit.Commit(self._git, self._id)
        diff_text = current_commit.diff(self._diff_lines_count_edit.value())
        self._diff_view.setPlainText(diff_text)

        self._files_list.clear()
        for file_name in current_commit.changed_files():
            self._files_list.addItem(QtWidgets.QListWidgetItem(file_name))

    def _select_file(self, item):
        doc = self._diff_view.document()
        cursor = doc.find(QRegExp("a/" + item.text()))
        cursor.movePosition(QTextCursor.StartOfLine)
        self._diff_view.setTextCursor(cursor)
        self._diff_view.centerCursor()