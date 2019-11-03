from .mapper import Mapper


class Metaclass(type):

    def __call__(cls, *args, **kwargs):
        obj = cls.__new__(cls,*args, **kwargs)
        args_list = list(args)
        if Mapper.exist(cls):
            params = Mapper.get_params(cls)
            args_list.extend(params)
        obj.__init__(*args_list, **kwargs)
        return obj