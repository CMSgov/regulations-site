from unittest import TestCase
from mock import Mock, patch

from django.test import RequestFactory

from regulations.generator.node_types import EMPTYPART, INTERP, REGTEXT
from regulations.views import partial

class PartialSectionViewTests(TestCase):
    @patch('regulations.generator.generator.get_tree_paragraph')
    @patch('regulations.views.partial.navigation')
    @patch('regulations.generator.generator.api_reader.ApiReader')
    def test_get_context_data(self, ApiReader, navigation, get_tree_paragraph):
        ApiReader.return_value.layer.return_value = {'layer': 'layer'}
        navigation.nav_sections.return_value = None, None
        get_tree_paragraph.return_value = {
            'text': 'Some Text',
            'children': [],
            'label': ['205'],
            'node_type': REGTEXT
        }

        reg_part_section = '205'
        reg_version = '2013-10608'

        request = RequestFactory().get('/fake-path/?layers=meta')
        view = partial.PartialSectionView.as_view(
            template_name='regulations/regulation-content.html')

        response = view(request, label_id=reg_part_section,
                        version=reg_version)
        root = response.context_data['tree']
        subpart = root['children'][0]
        self.assertEqual(subpart['children'][0],
                         get_tree_paragraph.return_value)
