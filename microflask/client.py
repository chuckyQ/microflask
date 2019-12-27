import json
import requests
import warnings

__all__ = ['RPC', 'help']

def _get(ns, attr, host, port, magic=None, args=tuple(), **kwargs):

    d = dict(namespace=ns, attr=attr, args=args, kwargs=kwargs, magic=magic)

    resp = requests.get(f'{host}:{port}', json=json.dumps(d))

    data = resp.json()

    if data['deprecated']: warnings.warn(data['deprecation_message'], category=DeprecationWarning, stacklevel=1)
    
    if data['error']: 
        
        err = type(data['error_type'], (Exception,), dict())
        
        raise err(data['error_message'])
    
    return data['data']
        
class Partial():

    def __init__(self, namespace: str, attr: str, host: str, port: int):

        self._namespace = namespace
        self._attr = attr
        self._host = host
        self._port = port

    def __call__(self, *args, **kwargs):

        return _get(ns=self._namespace, attr=self._attr, 
                   host=self._host, port=self._port, args=args, **kwargs)

class RPC():

    def __init__(self, namespace, host, port):

        self._namespace = namespace
        self._host = host
        self._port = port
        self._attr = None
        self._attrs = set()

        self._attrs.update(dir(self))

    def __getattr__(self, attr):

        if attr not in self._attrs:

            raise AttributeError(f'Module {self._namespace} has no attribute {attr!r}')
        
        return Partial(namespace=self._namespace, attr=attr, host=self._host, port=self._port)    

    def __dir__(self):

        if not self._attrs:

            return _get(ns=self._namespace, attr=None, 
                        host=self._host, port=self._port, magic='dir', 
                        )

        return sorted(self._attrs)

    def __repr__(self):

        return f'{self.__class__.__name__}(namespace={self._namespace!r}, host={self._host!r}, port={self._port})'

def help(obj):

    h = _get(ns=obj._namespace, attr=obj._attr, 
             host=obj._host, port=obj._port, magic='help')

    print(h)
