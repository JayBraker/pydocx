# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from itertools import islice

from pydocx.models import XmlModel, XmlCollection, XmlChild
from pydocx.openxml.wordprocessing.run_properties import RunProperties
from pydocx.openxml.wordprocessing.br import Break
from pydocx.openxml.wordprocessing.drawing import Drawing
from pydocx.openxml.wordprocessing.picture import Picture
from pydocx.openxml.wordprocessing.no_break_hyphen import NoBreakHyphen
from pydocx.openxml.wordprocessing.text import Text
from pydocx.openxml.wordprocessing.tab_char import TabChar
from pydocx.openxml.wordprocessing.deleted_text import DeletedText
from pydocx.openxml.wordprocessing.footnote_reference import FootnoteReference
from pydocx.openxml.wordprocessing.footnote_reference_mark import FootnoteReferenceMark  # noqa


class Run(XmlModel):
    XML_TAG = 'r'

    properties = XmlChild(type=RunProperties)

    children = XmlCollection(
        TabChar,
        Break,
        NoBreakHyphen,
        Text,
        Drawing,
        Picture,
        DeletedText,
        FootnoteReference,
        FootnoteReferenceMark,
    )

    def get_style_chain_stack(self):
        if not self.properties:
            return

        parent_style = self.properties.parent_style
        if not parent_style:
            return

        # TODO the getattr is necessary because of footnotes. From the context
        # of a footnote, a paragraph's container is the footnote part, which
        # doesn't have access to the style_definitions_part
        part = getattr(self.container, 'style_definitions_part', None)
        if part:
            style_stack = part.get_style_chain_stack('character', parent_style)
            for result in style_stack:
                yield result

    def _get_properties_inherited_from_parent_paragraph(self):
        from pydocx.openxml.wordprocessing.paragraph import Paragraph

        inherited_properties = {}

        nearest_paragraphs = self.nearest_ancestors(Paragraph)
        # TODO use get_first_from_sequence utility?
        parent_paragraph = list(islice(nearest_paragraphs, 0, 1))
        if parent_paragraph:
            parent_paragraph = parent_paragraph[0]
            style_stack = parent_paragraph.get_style_chain_stack()
            for style in reversed(list(style_stack)):
                if style.run_properties:
                    inherited_properties.update(
                        dict(style.run_properties.fields),
                    )
        return inherited_properties

    def _get_inherited_properties_from_parent_style(self):
        inherited_properties = {}
        style_stack = self.get_style_chain_stack()
        for style in reversed(list(style_stack)):
            if style.run_properties:
                inherited_properties.update(
                    dict(style.run_properties.fields),
                )
        return inherited_properties

    @property
    def inherited_properties(self):
        properties = {}
        properties.update(
            self._get_properties_inherited_from_parent_paragraph(),
        )
        properties.update(
            self._get_inherited_properties_from_parent_style(),
        )
        return RunProperties(**properties)

    @property
    def effective_properties(self):
        inherited_properties = self.inherited_properties
        effective_properties = {}
        effective_properties.update(dict(inherited_properties.fields))
        if self.properties:
            effective_properties.update(dict(self.properties.fields))
        return RunProperties(**effective_properties)
