from copy import deepcopy
from tvb_scripts.utils.log_error_utils import warning
from tvb_scripts.utils.data_structures_utils import labels_to_inds
from tvb.basic.neotraits.api import HasTraits, Attr


class BaseModel(HasTraits):

    filepath = Attr(
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

    @classmethod
    def from_tvb_instance(cls, instance, **kwargs):
        result = cls()
        attributes = instance.__dict__
        attributes.update(**kwargs)
        result = result.set_attributes(result, attributes)
        result.configure()
        return result

    @classmethod
    def from_tvb_file(cls, filepath, **kwargs):
        kwargs["filepath"] = filepath
        result = cls.from_tvb_instance(cls.from_file(filepath), **kwargs)
        return result

    @staticmethod
    def labels2inds(all_labels, labels):
        return labels_to_inds(all_labels, labels)

