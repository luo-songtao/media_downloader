

class Mapper(object):

    __mapper_relation = {}

    @staticmethod
    def register(cls, *params):
        Mapper.__mapper_relation[cls] = params

    @staticmethod
    def exist(cls):
        if cls in Mapper.__mapper_relation:
            return True
        else:
            return False

    @staticmethod
    def get_params(cls):
        return Mapper.__mapper_relation[cls]
