from datetime import datetime

from django.views.generic.base import TemplateView

from regulations.generator.api_reader import ApiReader
from regulations.generator import versions


class SearchView(TemplateView):
    client = ApiReader()

    template_name = 'regulations/search.html'

    def accumulate_results(self, results, current_page=0):
        response = self.client.search(self.request.GET.get("q"), page=current_page)
        if not response['results']:
            return results
        return self.accumulate_results(results + response['results'], current_page=current_page+1)

    def get_data(self):
        return self.accumulate_results([])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_versions = versions.fetch_regulations_and_future_versions()
        results = self.get_data()
        context['results'] = list(get_current_results(results, all_versions))
        return {**context, **self.request.GET.dict()}


def get_current_results(results, versions):
    for result in results:
        if is_current(result, versions[result['regulation']]):
            yield result

def is_current(result, versions):
    return result['version'] == get_current_version(versions)


def get_current_version(versions):
    today = datetime.today()
    for version in versions:
        if version['by_date'] <= today:
            return version['version']
    return None
