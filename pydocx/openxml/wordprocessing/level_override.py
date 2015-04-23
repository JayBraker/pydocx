# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlChild, XmlAttribute


class LevelOverride(XmlModel):
    level_id = XmlAttribute(name='ilvl')
    start_override = XmlChild(name='startOverride', attrname='val')
