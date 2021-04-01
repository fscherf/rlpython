import gc


def get_objects_by_class(object_class):
    objects = []

    for obj in gc.get_objects():
        if isinstance(obj, object_class):
            objects.append(obj)

    return objects


def get_object_by_id(object_id):
    object_id = str(object_id)

    for obj in gc.get_objects():
        if str(id(obj)) == object_id:
            return obj
