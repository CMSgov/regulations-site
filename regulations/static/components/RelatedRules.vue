<template>
    <div>
        <related-rule-list :rules="rules"></related-rule-list>
    </div>
</template>

<script>
import RelatedRuleList from './RelatedRuleList.vue'
export default {
    components: {
        RelatedRuleList,
    },
    
    props: {
        url: {
            type: String,
            required: true,
        },
    },
    
    data() {
        return {
            rules: null,
        }
    },

    async created() {
        this.rules = await this.fetch_rules(this.url);
    },
    
    methods: {
        async fetch_rules(url) {
            const response = await fetch(url);
            const rules = await response.json();
            return rules.results;
        }
    }
};
</script>
