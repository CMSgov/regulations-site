import RelatedRules from '../components/RelatedRules.vue';

export default {
  title: 'SupplementaryContent/Related Rules',
  component: RelatedRules,
};

const Template = (args, { argTypes }) => ({
  props: Object.keys(argTypes),
  components: { RelatedRules },
  template: '<related-rules v-bind="$props" ></related-rules>',
});

export const Basic = Template.bind({});
Basic.args = {
    "url": "https://www.federalregister.gov/api/v1/documents.json?fields[]=type&fields[]=abstract&fields[]=citation&fields[]=correction_of&fields[]=dates&fields[]=docket_id&fields[]=docket_ids&fields[]=document_number&fields[]=effective_on&fields[]=html_url&fields[]=publication_date&fields[]=regulation_id_number_info&fields[]=regulation_id_numbers&fields[]=title&per_page=20&conditions[type][]=RULE&conditions[cfr][title]=42&conditions[cfr][part]=433",
};