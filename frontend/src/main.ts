import { createApp } from "vue";
import { createPinia } from "pinia";

import App from "./App.vue";
import { vReveal } from "./directives/reveal";
import { vRipple } from "./directives/ripple";
import { vTilt } from "./directives/tilt";
import router from "./router";
import "./styles/main.css";

const app = createApp(App);
app.directive("reveal", vReveal);
app.directive("tilt", vTilt);
app.directive("ripple", vRipple);
app.use(createPinia()).use(router).mount("#app");
