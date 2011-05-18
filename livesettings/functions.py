from django.utils.translation import ugettext
from livesettings import values
from livesettings.exceptions import SettingNotSet
from livesettings.utils import is_string_like

import logging
import warnings

log = logging.getLogger('configuration')

_NOTSET = object()

class ConfigurationSettings(object):
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        # for backwards compatibility, make this a singleton.
        if ConfigurationSettings._instance is None:
            instance = ConfigurationSettings._instance = super(ConfigurationSettings, cls).__new__(cls, *args, **kwargs)
            instance.settings = values.SortedDotDict()
            instance.prereg = {}
        else:
            warnings.warn("The ConfigurationSettings singleton is deprecated. Use livesettings.configuration_settings instead", DeprecationWarning)
        return ConfigurationSettings._instance
    
    def __getitem__(self, key):
        """Get an element either by ConfigurationGroup object or by its key"""
        key = self._resolve_key(key)
        return self.settings.get(key)

    def __getattr__(self, key):
        """Get an element either by ConfigurationGroup object or by its key"""
        try:
            return self[key]
        except KeyError:
            raise AttributeError, key

    def __iter__(self):
        for v in self.groups():
            yield v

    def __len__(self):
        return len(self.settings)

    def __contains__(self, key):
        key = self._resolve_key(key)
        return key in self.settings

    def _resolve_key(self, raw):
        if is_string_like(raw):
            key = raw

        elif isinstance(raw, values.ConfigurationGroup):
            key = raw.key

        else:
            group = self.groups()[raw]
            key = group.key

        return key

    def get_config(self, group, key):
        try:
            if isinstance(group, values.ConfigurationGroup):
                group = group.key

            cg = self.settings.get(group, None)
            if not cg:
                raise SettingNotSet('%s config group does not exist' % group)

            else:
                return cg[key]
        except KeyError:
            raise SettingNotSet('%s.%s' % (group, key))
    
    def groups(self):
        """Return ordered list"""
        values = self.settings.values()
        values.sort()
        return values

    def has_config(self, group, key):
        if isinstance(group, values.ConfigurationGroup):
            group = group.key

        cfg = self.settings.get(group, None)
        if cfg and key in cfg:
            return True
        else:
            return False

    def preregister_choice(self, group, key, choice):
        """Setup a choice for a group/key which hasn't been instantiated yet."""
        k = (group, key)
        if self.prereg.has_key(k):
            self.prereg[k].append(choice)
        else:
            self.prereg[k] = [choice]

    def register(self, value):
        g = value.group
        if not isinstance(g, values.ConfigurationGroup):
            raise ValueError('value.group should be an instance of ConfigurationGroup')

        groupkey = g.key
        valuekey = value.key

        k = (groupkey, valuekey)
        if self.prereg.has_key(k):
            for choice in self.prereg[k]:
                value.add_choice(choice)

        if not groupkey in self.settings:
            self.settings[groupkey] = g

        self.settings[groupkey][valuekey] = value

        return value
    
    def __unicode__(self):
        return u"ConfigurationSettings: " + unicode(self.groups())

configuration_settings = ConfigurationSettings()


def config_exists(group, key):
    """Test to see if a setting has been registered"""

    return configuration_settings.has_config(group, key)

def config_get(group, key):
    """Get a configuration setting"""
    try:
        return configuration_settings.get_config(group, key)
    except SettingNotSet:
        log.debug('SettingNotSet: %s.%s', group, key)
        raise

def config_get_group(group):
    return configuration_settings[group]

def config_collect_values(group, groupkey, key, unique=True, skip_missing=True):
    """Look up (group, groupkey) from config, then take the values returned and
    use them as groups for a second-stage lookup.

    For example:

    config_collect_values(PAYMENT, MODULES, CREDITCHOICES)

    Stage 1: ['PAYMENT_GOOGLE', 'PAYMENT_AUTHORIZENET']
    Stage 2: config_value('PAYMENT_GOOGLE', 'CREDITCHOICES')
           + config_value('PAYMENT_AUTHORIZENET', 'CREDITCHOICES')
    Stage 3: (if unique is true) remove dupes
    """
    groups = config_value(group, groupkey)

    ret = []
    for g in groups:
        try:
            ret.append(config_value(g, key))
        except KeyError:
            if not skip_missing:
                raise SettingNotSet('No config %s.%s' % (g, key))

    if unique:
        out = []
        for x in ret:
            if not x in out:
                out.append(x)
        ret = out

    return ret

def config_register(value):
    """Register a value or values.

    Parameters:
        -A Value
    """
    return configuration_settings.register(value)

def config_register_list(*args):
    for value in args:
        config_register(value)

def config_value(group, key, default=_NOTSET):
    """Get a value from the configuration system"""
    try:
        return config_get(group, key).value
    except SettingNotSet:
        if default != _NOTSET:
            return default
        raise

def config_value_safe(group, key, default_value):
    """Get a config value with a default fallback, safe for use during SyncDB."""
    raw = default_value

    try:
        raw = config_value(group, key)
    except SettingNotSet:
        pass
    except ImportError:
        log.warn("Error getting %s.%s, OK if you are in SyncDB.", group, key)

    return raw


def config_choice_values(group, key, skip_missing=True, translate=False):
    """Get pairs of key, label from the setting."""
    try:
        cfg = config_get(group, key)
        choices = cfg.choice_values

    except SettingNotSet:
        if skip_missing:
            return []
        else:
            raise SettingNotSet('%s.%s' % (group, key))

    if translate:
        choices = [(k, ugettext(v)) for k, v in choices]

    return choices

def config_add_choice(group, key, choice):
    """Add a choice to a value"""
    if config_exists(group, key):
        cfg = config_get(group, key)
        cfg.add_choice(choice)
    else:
        configuration_settings.preregister_choice(group, key, choice)
