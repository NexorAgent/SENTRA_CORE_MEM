import importlib
from fastapi import FastAPI


def test_scripts_api_app():
    mod = importlib.import_module('scripts.api_sentra')
    assert isinstance(getattr(mod, 'app', None), FastAPI)


def test_root_api_wrapper():
    mod_root = importlib.import_module('api_sentra')
    mod_script = importlib.import_module('scripts.api_sentra')
    assert mod_root.app is mod_script.app
