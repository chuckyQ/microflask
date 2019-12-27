Quickstart
==========

Say we have a module called ``mymodule`` on the server defined as follows::

    """This is the module level docstring"""

    def bar(a: int, b: int):
        """This is a help message for bar"""

        return a - b

    def foo(a, b):
        
        return a + b    

On the server side, we register the module and run the server::

    import microflask

    microflask.register('mymodule')

    microflask.run()

On the client side::

    from microflask import RPC

    # host and port values are the default for flask
    rpc = RPC('mymodule', host='http://127.0.0.1', port=5000) 

    print(rpc.bar(20, 10)) # prints 10

Very straightforward, but sometimes we forget what is actually located in a namespace,
so Python comes with a ``dir`` function and a ``help`` function to display the available
objects in a module and give descriptions. ``microflask`` also has these capabilities.
The ``__dir__`` attribute has been overloaded to list out what is available in the remote
module, and there is a help function in ``microflask`` to give the useful docstring of the
function or module.

.. note::

    Only functions are visible on the client side when ``dir`` is called.

.. code::

    >>> from microflask import RPC, help
    >>> # host and port values are the default for flask
    >>> rpc = RPC('mymodule', host='http://127.0.0.1', port=5000) 

Running this module with the ``-i`` option for the interpreter, we can use the help function 
to read the docstring for a module.

>>> help(rpc) # Prints the module level help message
>>> help(rpc.bar) # Prints the function help message
