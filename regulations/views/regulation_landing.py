from datetime import date, datetime
from requests import HTTPError
from django.views.generic.base import TemplateView
from django.http import Http404
from django.urls import reverse

from regulations.views.mixins import TableOfContentsMixin
from regulations.generator import api_reader
from regulations.views.errors import NotInSubpart
from regulations.views.utils import find_subpart

client = api_reader.ApiReader()


class RegulationLandingView(TableOfContentsMixin, TemplateView):

    template_name = "regulations/regulation_landing.html"

    sectional_links = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        reg_part = self.kwargs.get("part")

        try:
            current = client.toc(date.today(), 42, reg_part)
        except HTTPError:
            raise Http404

        parts = client.effective_parts(date.today())
        reg_version = current['date']
        toc = current['toc']
        part_label = toc['label_description']

        c = {
            'toc': toc,
            'version': reg_version,
            'part': reg_part,
            'part_label': part_label,
            'reg_part': reg_part,
            'parts': parts,
            'last_updated': datetime.fromisoformat(current['last_updated']),
            'left_sidebar_content': 'regulations/partials/left_sidebar_views/subpart_view.html',
            'content': [
                'regulations/partials/landing_%s.html' % reg_part,
                'regulations/partials/landing_default.html',
            ],
        }

        self.build_toc_urls(c, toc)

        return {**context, **c}

    def build_toc_url(self, context, toc, node):
        url_kwargs = {
            'part': context['part'],
            'version': context['version'],
        }

        if node['type'] == 'subpart':
            url_kwargs['subpart'] = 'Subpart-{}'.format(node['identifier'][0])
        elif node['type'] == 'section':
            try:
                subpart = find_subpart(node['identifier'][1], toc)
                if subpart is not None:
                    url_kwargs['subpart'] = 'Subpart-{}'.format(subpart)
            except NotInSubpart:
                pass

        return reverse('reader_view', kwargs=url_kwargs)
