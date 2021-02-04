# -*- coding: utf-8 -*-
from django.http import Http404
from django.views.generic.base import TemplateView

from regulations.generator import generator
from regulations.generator.html_builder import CFRHTMLBuilder
from regulations.generator.node_types import EMPTYPART, REGTEXT, label_to_text
from regulations.views import navigation, utils


class PartialView(TemplateView):
    """Base class of various partial markup views. sectional_links indicates
    whether this view should use section links (url to a path) or just hash
    links (to an anchor on the page)"""

    sectional_links = True

    def determine_layers(self, label_id, version):
        """Figure out which layers to apply by checking the GET args"""
        return generator.layers(
            utils.layer_names(self.request), 'cfr', label_id,
            self.sectional_links, version)

    def get_context_data(self, **kwargs):
        context = super(PartialView, self).get_context_data(**kwargs)

        label_id = context['label_id']
        version = context['version']

        tree = generator.get_tree_paragraph(label_id, version)
        if tree is None:
            raise Http404

        layers = list(self.determine_layers(label_id, version))
        builder = CFRHTMLBuilder(layers)
        builder.tree = tree
        builder.generate_html()
        return self.transform_context(context, builder)


class PartialSectionView(PartialView):
    """ Single section of reg text """
    template_name = 'regulations/regulation-content.html'

    def section_navigation(self, label, version):
        nav_sections = navigation.nav_sections(label, version)
        if nav_sections:
            p_sect, n_sect = nav_sections

            return {'previous': p_sect, 'next': n_sect,
                    'page_type': 'reg-section'}

    def transform_context(self, context, builder):
        child_of_root = builder.tree
        #   Add a layer to account for subpart if this is regtext
        if builder.tree['node_type'] == REGTEXT:
            child_of_root = {
                'node_type': EMPTYPART,
                'children': [builder.tree]}
        context['markup_page_type'] = 'reg-section'
        context['tree'] = {'children': [child_of_root]}
        context['navigation'] = self.section_navigation(
            context['label_id'], context['version'])

        return context

class PartialDefinitionView(PartialView):
    """ Single paragraph of a regtext formatted for display
        as an inline interpretation """

    template_name = "regulations/partial-definition.html"

    def transform_context(self, context, builder):
        context['node'] = builder.tree
        context['formatted_label'] = label_to_text(
            builder.tree['label'], True, True)
        context['node']['section_id'] = '%s-%s' % (
            builder.tree['label'][0], builder.tree['label'][1])
        return context

class PartialRegulationView(PartialView):
    """ Entire regulation without chrome """

    template_name = 'regulations/regulation-content.html'
    sectional_links = False

    def transform_context(self, context, builder):
        context['tree'] = builder.tree
        return context
