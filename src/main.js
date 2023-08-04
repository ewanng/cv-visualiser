import Vue from "vue";
import App from "./App.vue";
import axios from "axios";
import VueAxios from "vue-axios";
import { BootstrapVue, BootstrapVueIcons, IconsPlugin } from "bootstrap-vue";
import VueApexCharts from "vue-apexcharts";

import "bootstrap/dist/css/bootstrap.css";
import "bootstrap-vue/dist/bootstrap-vue.css";

Vue.use(VueApexCharts);
Vue.use(BootstrapVue);
Vue.use(IconsPlugin);
Vue.use(BootstrapVueIcons);
Vue.use(VueAxios, axios);

Vue.component("ApexChart", VueApexCharts);
Vue.config.productionTip = false;

Vue.prototype.$apiKey = "***********************************";
Vue.prototype.$apiUrl = "************************************************";
Vue.prototype.$apiEnv = "DEV";

require("./assets/CSS/ComponentCSS.css");
new Vue({
  render: (h) => h(App),
}).$mount("#app");
