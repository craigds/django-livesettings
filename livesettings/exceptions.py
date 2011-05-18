
class SettingNotSet(Exception):
    def __init__(self, k, cachekey=None):
        self.key = k
        self.cachekey = cachekey
        self.args = [self.key, self.cachekey]
