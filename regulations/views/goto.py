from requests import HTTPError

from django.urls import reverse
from django.http import Http404
from django.views.generic.base import RedirectView

from regulations.views.utils import find_subpart
from regulations.views.mixins import TableOfContentsMixin
from regulations.views.errors import NotInSubpart
from regulations.generator import api_reader

client = api_reader.ApiReader()


class GoToRedirectView(TableOfContentsMixin, RedirectView):

    permanent = False
    pattern_name = 'reader_view'

    def get_redirect_url(self, *args, **kwargs):
        kwargs = self.request.GET.dict()
        
        url_kwargs = {
                "part": kwargs.get("part"),
        }

        if kwargs.get("section") is not None and kwargs.get("section") != "":
            url_kwargs["section"] = kwargs.get("section")

            if kwargs.get(f'{kwargs.get("part")}-version') is not None:
                url_kwargs["version"] = kwargs.get(f'{kwargs.get("part")}-version')

        citation = [url_kwargs["part"]]
        if url_kwargs.get("section"):
            citation.append(url_kwargs["section"])

        url = reverse(self.pattern_name, kwargs=url_kwargs) + "#" + "-".join(citation)
        return url

