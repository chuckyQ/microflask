import importlib
import json

from io import StringIO
from contextlib import redirect_stdout
from types import FunctionType

from flask import Flask
from flask import request
from flask import jsonify

__all__ = ['register', 'run']

_dispatch = dict()

IMPORTED_MODULES = dict()

app = Flask(__name__)

def error(response, error_type, error_message):

    response.update(error=True, error_type=error_type.__name__, error_message=error_message)
    return jsonify(response)

def register(module):
    """Function to register the string ``module`` in 
    the the namespace
    """

    mod = importlib.import_module(module)

    IMPORTED_MODULES[module] = mod

    if not _dispatch.get(module):

        _dispatch[module] = dict()

    for key, val in vars(mod).items():

        if isinstance(val, FunctionType):

            _dispatch[module][key] = val

def handle_magic(response, req, attr, magic):

    if req["namespace"] not in list(_dispatch.keys()):

        return error(response, LookupError, f'No module named {req["namespace"]!r}')

    if magic == 'dir':

        response['data'] = [x for x in _dispatch[req['namespace']]]
            
    elif magic == 'help':

        f = StringIO()

        obj = IMPORTED_MODULES.get(req['namespace'])

        if obj is None: 
            
            return error(response, LookupError, f'No module named {req["namespace"]!r} exists.')

        if attr is not None:

            _attr = getattr(obj, attr, None)

        else: 

            _attr = obj

        if _attr is None: 
            
            return error(response, AttributeError, f'No attribute {attr!r} in module {obj!r}')

        with redirect_stdout(f):

            help(_attr)

        response['data'] = f.getvalue()

    else:

        return error(response, ValueError, f'Undefined magic code {magic!r}')       
    
    return jsonify(response)

def run(*args, **kwargs):

    app.run(*args, **kwargs)

@app.route('/', methods=['GET'])
def _main():

    response = {
        'data' : None,
        'deprecated' : False,
        'error' : False,
        'error_type': None,
        'deprecation_message' : '',
        'error_message' : '',
    }

    j = request.get_json()

    if j is None:

        return error(response, ValueError, 'No data received')

    req = json.loads(j)

    ns = req.get('namespace')

    if ns is None:

        return error(response, ValueError, f'No namespace supplied')

    magic = req.get('magic')

    if magic is not None:

        return handle_magic(response=response, req=req, attr=req['attr'], magic=magic)

    try:

        if _dispatch.get(ns) is None: 

            return error(response, LookupError, f'The namespace {ns!r} does not exist.')

        else:   

            func = _dispatch[ns].get(req['attr'])

            if func is None:

                return error(response, AttributeError, f'Module {ns!r} has no attribute {req["attr"]!r}')

            try:

                response.update(data=func(*req['args'], **req['kwargs']))

            except BaseException as e:

                # The error is an instance of an exception so I need the class name
                # for proper error reporting
                return error(response, error_type=e.__class__, error_message=e.args[0])

    except KeyError:

        return error(response, ImportError, 'Invalid key, verify it is hashable')
    
    return jsonify(response)

