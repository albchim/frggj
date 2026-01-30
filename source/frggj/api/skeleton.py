# skeleton
from frggj.api.io import import_skeleton


class GSkeleton(object):
    def __init__(self, parent):
        self._parent = parent
        self._influences = None
        self._bindpose = None

    def set_bindpose(self, bindpose):
        self._bindpose = bindpose

    def set_influences(self, influences):
        self._influences = influences

    def get_bindpose(self):
        return self._bindpose

    def get_influences(self):
        return self._influences

    def load(self, filepath):
        self._influences, self._bindpose = import_skeleton(filepath)
