from copy import deepcopy
from tvb_scripts.utils.log_error_utils import warning
from tvb.basic.neotraits.api import HasTraits, Attr


class Base(HasTraits):

    file_path = Attr(
        field_type=str,
        label="File path",
        default='', required=False,
        doc="Absolute path to the object's location in the file system")

    def set_attributes(self, **kwargs):
        for attr, value in kwargs.items():
            try:
                if len(value):
                    setattr(self, attr, value)
            except:
                warning("Failed to set attribute %s to %s!" % (attr, self.__class__.__name__))
        return self

    @staticmethod
    def from_instance(instance, **kwargs):
        result = deepcopy(instance)
        result = result.set_attributes(result, **kwargs)
        result.configure()
        return result

    # TODO: Fix this!
    @classmethod
    def from_tvb_instance(cls, instance, **kwargs):
        result = cls()
        result.file_path = kwargs.pop("file_path", "")
        attributes = instance.__dict__
        attributes.update(**kwargs)
        result = result.set_attributes(result, attributes)
        result.configure()
        return result
