from datetime import date

from django.conf import settings
from django.http import Http404
from django.views.generic.base import TemplateView

from regulations.generator import generator
from regulations.generator.versions import fetch_grouped_history
from regulations.views import utils
from regulations.views.diff import PartialSectionDiffView
from regulations.views.landing import get_versions, regulation as landing_page
from regulations.views.partial import *
from regulations.views.partial_search import PartialSearch
from regulations.views.sidebar import SideBarView


class ChromeView(TemplateView):
    """ Base class for views which wish to include chrome. """
    template_name = 'chrome.html'

    def get(self, request, *args, **kwargs):
        """Override GET so that we can catch and propagate any errors in the
        included partial(s)"""

        try:
            return super(ChromeView, self).get(request, *args, **kwargs)
        except BadComponentException, e:
            return e.response

    def _assert_good(self, response):
        if response.status_code != 200:
            raise BadComponentException(response)

    def add_extras(self, context):
        context['env'] = 'source' if settings.DEBUG else 'built'
        context['GOOGLE_ANALYTICS_SITE'] = settings.GOOGLE_ANALYTICS_SITE
        context['GOOGLE_ANALYTICS_ID'] = settings.GOOGLE_ANALYTICS_ID
        return context

    def process_partial(self, context):
        partial_view = self.partial_class.as_view()
        response = partial_view(self.request,
                                label_id=context['label_id'],
                                version=context['version'])
        self._assert_good(response)
        response.render()
        return response.content

    def get_context_data(self, **kwargs):
        context = super(ChromeView, self).get_context_data(**kwargs)

        label_id = context['label_id']
        version = context['version']

        #   Hack solution: pull in full regulation, then the partial
        #   @todo: just query the meta and toc layers
        part = label_id.split('-')[0]
        full_tree = generator.get_regulation(part, version)
        relevant_tree = generator.get_tree_paragraph(label_id, version)

        if full_tree is None or relevant_tree is None:
            raise Http404

        context['partial_content'] = self.process_partial(context)

        sidebar_view = SideBarView.as_view()
        response = sidebar_view(self.request, label_id=label_id,
                                version=version)
        self._assert_good(response)
        response.render()
        context['sidebar_content'] = response.content

        appliers = utils.handle_specified_layers(
            'toc,meta', part, version, self.partial_class.sectional_links)
        builder = generate_html(full_tree, appliers)

        context['tree'] = full_tree
        self.add_extras(context)

        context['part'] = part
        context['history'] = fetch_grouped_history(part)

        context['ranges'] = self.generate_ranges(context['history'])
        context['today'] = date.today()

        return context

    def generate_ranges(self, history):
        """To generate a select box for dates, we need a range of years,
        months, dates, etc."""
        earliest = [v['by_date'] for v in history]
        earliest = sorted(earliest)
        today = date.today()
        ranges = {'month': ('%02d' % m for m in range(1, 13)),
                  'day': ('%02d' % d for d in range(1, 32))}
        if not earliest:
            ranges['year'] = map(str, range(today.year + 10, 1979, -1))
        else:
            ranges['year'] = map(str, range(today.year + 10,
                                            earliest[0].year - 1, -1))
        return ranges


class ChromeInterpView(ChromeView):
    """Interpretation of regtext section/paragraph or appendix with chrome"""
    partial_class = PartialInterpView


class ChromeSectionView(ChromeView):
    """Regtext section with chrome"""
    partial_class = PartialSectionView


class ChromeParagraphView(ChromeView):
    """Regtext paragraph with chrome"""
    partial_class = PartialParagraphView


class ChromeRegulationView(ChromeView):
    """Entire regulation with chrome"""
    partial_class = PartialRegulationView


class ChromeSearchView(ChromeView):
    """Search results with chrome"""
    partial_class = PartialSearch

    def get(self, request, *args, **kwargs):
        """Override GET so that we can pull our the version"""

        kwargs['version'] = request.GET.get('version', '')
        return super(ChromeSearchView, self).get(request, *args, **kwargs)


class ChromeSectionDiffView(ChromeView):
    """Search results with chrome"""
    partial_class = PartialSectionDiffView

    def process_partial(self, context):
        """Must override the parameters to this partial as it needs to have
        a 'newer_version' field"""
        partial_view = self.partial_class.as_view()
        response = partial_view(self.request,
                                label_id=context['label_id'],
                                version=context['version'],
                                newer_version=context['newer_version'])
        self._assert_good(response)
        response.render()
        return response.content


class ChromeLandingView(ChromeView):
    """Landing page with chrome"""
    partial_class = PartialSectionView # Needed to know sectional status

    def process_partial(self, context):
        """Landing page isn't a TemplateView"""
        response = landing_page(self.request, context['regulation'])
        self._assert_good(response)
        return response.content

    def get(self, request, *args, **kwargs):
        """Override GET to add the version to chrome context"""
        current, _ = get_versions(kwargs['label_id'])
        kwargs['version'] = current['version']
        # Use the first section for the chrome -- does not work in all regs
        kwargs['regulation'] = kwargs['label_id']
        kwargs['label_id'] = kwargs['label_id'] + '-1'
        return super(ChromeLandingView, self).get(request, *args, **kwargs)


class BadComponentException(Exception):
    """Allows us to propagate errors in loaded partials"""
    def __init__(self, response):
        self.response = response

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return "BadComponentException(response=%s)" % repr(self.response)
