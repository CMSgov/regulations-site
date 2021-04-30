from datetime import date
import logging

from django.views.generic.base import TemplateView
from requests import HTTPError

from regulations.generator import api_reader


logger = logging.getLogger(__name__)

client = api_reader.ApiReader()


class HomepageView(TemplateView):

    template_name = 'regulations/homepage.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        c = {}
        try:
            today = date.today()
            parts = client.v2_effective_parts(today)
            if not parts:
                return context

            c = {
                'regulations': parts,
                'cfr_title_text': parts[0]['structure']['label_description'],
                'cfr_title_number': parts[0]['structure']['identifier'],
            }
        except HTTPError:
            logger.warning("NOTE: eRegs homepage loaded without any stored regulations.")

        return {**context, **c}
