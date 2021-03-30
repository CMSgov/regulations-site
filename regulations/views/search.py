from datetime import datetime

from django.views.generic.base import TemplateView

from regulations.generator.api_reader import ApiReader
from regulations.generator import versions


class SearchView(TemplateView):
    client = ApiReader()

    template_name = 'regulations/search.html'

    def get_data(self):
        result = self.client.search(self.request.GET.get("q"))
        if result['total_hits'] > len(result['results']):
            i = 1
            while next := self.client.search(self.request.GET.get("q"), page=i)['results']:
                result['results'] = result['results'] + next
                i += 1
        return result

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_versions = versions.fetch_regulations_and_future_versions()
        # I feel like this makes more sense elsewhere in the class flow
        results = self.get_data()
        # This is mixing tenses
        results['results'] = list((result for result in results['results'] if is_current(result, all_versions[result['regulation']])))
        return {**context, **results, **self.request.GET.dict()}

def is_current(result, versions):
    return result['version'] == get_current_version(versions)

def get_current_version(versions):
    today = datetime.today()
    for version in versions:
        if version['by_date'] <= today:
            return version['version']
    return None
