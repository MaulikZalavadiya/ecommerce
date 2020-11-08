from django import template

register = template.Library()


@register.simple_tag
def to_dict(value):
    """converts string  to dict"""
    return eval(value)

@register.simple_tag
def to_str(value):
    """converts string  to dict"""
    return str(value)


@register.simple_tag
def listConverter(value):
    listConverter = list(str(value[1:len(value) - 1]).split(","))
    print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@", listConverter)

    return listConverter


@register.filter(name='split')
def split(value, key):
    return value.split(key)

@register.simple_tag
def sizequantity(size,qunatity):
    size = list(str(size[1:len(size) - 1]).split(","))
    qunatity = list(str(qunatity[1:len(qunatity) - 1]).split(","))

    dict = {}
    lensize = len(size)
    for i in range(lensize):
        dict[size[i]]=qunatity[i]
    print(">>>>>>>>><<<<<<<MMMMMMMMMMMMMMMM???????????????",dict)
    return dict
