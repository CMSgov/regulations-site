define("search-view",["jquery","underscore","backbone"],function(e,t,n){var r=n.View.extend({el:"#search",events:{submit:"openSearchResults"},openSearchResults:function(t){sessionStorage.setItem("drawerDefault","search");if(window.history&&window.history.pushState){var n=e(t.target),r={};r.query=n.find("input[name=q]")[0].value,r.version=n.find("select[name=version]")[0].value}}});return r});