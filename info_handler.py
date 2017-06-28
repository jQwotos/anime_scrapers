import glob

# from .templates.module_search import ModuleSearch
from . import templates.module_search.ModuleSearch


class InfoHandler(ModuleSearch):

    def __init__(self):
        self.info_collector_location = "info_collectors/"
        self.modules = glob.glob("%s*.py" % (self.info_collector_location))
        self.modules = self._load_modules()

    def _search_module(self, query, strict, module):
        return module.search(query, strict)

    def search(self, query, strict=False):
        return [self._search_module(query, strict, x) for x in self.modules]

    def _details_module(self, id, module):
        return module.getDetailedInfo(id)

    def getDetailedInfo(self, id):
        return [self._details_module(id, x) for x in self.modules]


info_handler = InfoHandler()
