# from .util import make_class_dict

__version__ = "0.1.0"


# def datatype(_cls=None, *, expose=None):
#     def wrap(cls):
#         metacls = type(cls)

#         for ctor_name, ctor_args in cls.__annotations__.items():
#             ctor = metacls(ctor_name, (cls,), make_class_dict(ctor_args))

#             setattr(cls, ctor_name, ctor)

#             if expose is not None:
#                 expose[ctor_name] = ctor
#         return cls

#     if _cls is None:
#         return wrap
#     return wrap(_cls)


# def match(obj, cases):
#     for type, handler in cases.items():
#         if isinstance(obj, type):
#             return handler(*obj._bound_signature.args)
