from . import exceptions

def follow(dict_, path):
    if type(path) == str:
        path = path.split("/")

    current = dict_

    for name in path:
        if name in current:
            current = current[name]

        else:
            raise exceptions.NotFound()

    return current