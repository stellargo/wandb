"""
settings.
"""
import six
import logging

logger = logging.getLogger("wandb")

source = ("org", "team", "project", "env", "sysdir", "dir", "setup",
          "settings", "args")

defaults = dict(
    team=None,
    entity=None,
    project=None,
    base_url="https://api.wandb.ai",
    app_url="https://app.wandb.ai",
    api_key=None,
    anonymous=None,
    mode=None,
    group=None,
    job_type=None,

    # compatibility
    compat_version=None,  # set to "0.8" for safer defaults for older users
    strict=None,  # set to "on" to enforce current best practices (also "warn")

    # dynamic settings
    system_sample_seconds=2,
    system_samples=15,
    heartbeat_seconds=30,
    log_base_dir="wandb",
    log_dir="",
    log_user_spec="wandb-debug-{timespec}-{pid}-user.txt",
    log_internal_spec="wandb-debug-{timespec}-{pid}-internal.txt",
    log_user=False,
    log_internal=True,
    data_base_dir="wandb",
    data_dir="",
    data_spec="data-{timespec}-{pid}.dat",
    run_base_dir="wandb",
    run_dir_spec="run-{timespec}-{pid}",
)

move_mapping = dict(entity="team", )

deprecate_mapping = dict(entity=True, )

# env mapping?
env_prefix = "WANDB_"
env_settings = dict(
    team=None,
    entity=None,
    project=None,
    base_url=None,
    mode=None,
    group="WANDB_RUN_GROUP",
    job_type=None,
)


def _build_inverse_map(prefix, d):
    inv_map = dict()
    for k, v in six.iteritems(d):
        v = v or prefix + k.upper()
        inv_map[v] = k
    return inv_map


class Settings(object):
    def __init__(self, settings=None, environ=None, early_logging=None):
        _settings_dict = defaults.copy()
        # _forced_dict = dict()
        object.__setattr__(self, "_early_logging", early_logging)
        object.__setattr__(self, "_settings_dict", _settings_dict)
        # set source where force happened
        # object.__setattr__(self, "_forced_dict", _forced_dict)
        # set source where assignment happened
        # object.__setattr__(self, "_assignment_dict", _forced_dict)
        object.__setattr__(self, "_frozen", False)
        if settings:
            self.update(settings)
        if environ:
            inv_map = _build_inverse_map(env_prefix, env_settings)
            env_dict = dict()
            for k, v in six.iteritems(environ):
                if not k.startswith(env_prefix):
                    continue
                setting_key = inv_map.get(k)
                if setting_key:
                    env_dict[setting_key] = v
                else:
                    l = early_logging or logger
                    l.info("Unhandled environment var: {}".format(k))

            self.update(env_dict)

    def __copy__(self):
        s = Settings()
        s.update(dict(self))
        return s

    def _clear_early_logging(self):
        object.__setattr__(self, "_early_logging", None)

    def update(self, __d=None, **kwargs):
        if self._frozen and (__d or kwargs):
            raise TypeError('Settings object is frozen')
        d = __d or dict()
        for check in d, kwargs:
            for k in six.viewkeys(check):
                if k not in self._settings_dict:
                    raise KeyError(k)
        self._settings_dict.update(d)
        self._settings_dict.update(kwargs)

    def __getattr__(self, k):
        try:
            v = self._settings_dict[k]
        except KeyError:
            raise AttributeError(k)
        return v

    def __setattr__(self, k, v):
        if self._frozen:
            raise TypeError('Settings object is frozen')
        if k not in self._settings_dict:
            raise AttributeError(k)
        self._settings_dict[k] = v

    def keys(self):
        return self._settings_dict.keys()

    def __getitem__(self, k):
        return self._settings_dict[k]

    def freeze(self):
        object.__setattr__(self, "_frozen", True)
