from django.views.generic.base import (
    TemplateView,
    View,
)
from django.http import Http404
from django.urls import reverse
from django.http import HttpResponseRedirect

from regulations.generator import api_reader
from regulations.views import utils
from regulations.views.mixins import SidebarContextMixin, CitationContextMixin, TableOfContentsMixin
from regulations.views.utils import find_subpart


class ReaderView(TableOfContentsMixin, SidebarContextMixin, CitationContextMixin, TemplateView):

    template_name = 'regulations/reader.html'

    sectional_links = True

    client = api_reader.ApiReader()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        reg_version = context["version"]
        reg_part = context["part"]
        tree = self.client.v2_part(reg_version, 42, reg_part)

        structure = tree['structure']['children'][0]['children'][0]['children'][0]
        document = tree['document']

        self.build_toc_urls(context, structure)

        c = {
            'tree':         self.get_content(context, document, structure),
            'reg_part':     reg_part,
            'structure':    structure,
        }

        links = {}

        return {**context, **c, **links}


    def get_regulation(self, label_id, version):
        regulation = self.client.regulation(label_id, version)
        if regulation is None:
            raise Http404
        return regulation

    def get_view_links(self, context, toc):
        raise NotImplementedError()

    def get_versions(self, label_id):
        versions = self.client.regversions(label_id)
        if versions is None:
            raise Http404
        return versions['versions']

    def get_content(self, context, document, structure):
        raise NotImplementedError()


class PartReaderView(ReaderView):
    def get_view_links(self, context, toc):
        return {}
        part = context['part']
        version = context['version']
        first_subpart = utils.first_subpart(part, version)

        return {
            'subpart_view_link': reverse('reader_view', args=(part, first_subpart, version)),
        }

    def build_toc_url(self, context, node):
        return reverse('reader_view', args=(context['part'], context['version']))

    def get_content(self, context, document, structure):
        return document


class SubpartReaderView(ReaderView):
    def get_view_links(self, context, toc):
        part = context['part']
        version = context['version']
        subpart = context['subpart']

        section = utils.find_subpart_first_section(subpart, toc)
        if section is None:
            section = utils.first_section(part, version)
        citation = part + '-' + section

        return {
            'part_view_link': reverse('reader_view', args=(part, version)) + '#' + citation,
        }

    def get_content(self, context, document, structure):
        # using tree['structure'] find subpart requested then extract that data
        subpart = context['subpart']
        subpart_index = -1

        for i in range(len(structure['children'])):
            child = structure['children'][i]
            if 'type' in child and 'identifier' in child:
                if child['type'] == 'subpart' and "Subpart-{}".format(child['identifier'][0]) == subpart:
                    subpart_index = i

        if subpart_index == -1:
            raise Http404

        return document['children'][subpart_index]

    def build_toc_url(self, context, node):
        part = context['part']
        version = context['version']
        subpart = "Subpart-{}".format(node['identifier'][0] if node['type'] == 'subpart' else node['parent_subpart'])
        return reverse('reader_view', args=(part, subpart, version))


class SectionReaderView(TableOfContentsMixin, View):
    def get(self, request, *args, **kwargs):
        url_kwargs = {
            "part": kwargs.get("part"),
            "version": kwargs.get("version"),
        }

        client = api_reader.ApiReader()
        tree = self.client.v2_part(url_kwargs['version'], 42, url_kwargs['part'])
        structure = tree['structure']['children'][0]['children'][0]['children'][0]

        toc = self.get_toc(kwargs.get("part"), kwargs.get("version"))
        subpart = find_subpart(kwargs.get("section"), toc)

        if subpart is not None:
            url_kwargs["subpart"] = subpart

        url = reverse("reader_view", kwargs=url_kwargs)
        return HttpResponseRedirect(url)
