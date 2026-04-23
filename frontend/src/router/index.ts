import { createRouter, createWebHistory } from "vue-router";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      name: "home",
      component: () => import("../pages/HomePage.vue"),
    },
    {
      path: "/destinations",
      name: "destinations",
      component: () => import("../pages/DestinationPage.vue"),
    },
    {
      path: "/search",
      name: "search",
      component: () => import("../pages/SearchPage.vue"),
    },
    {
      path: "/routes",
      name: "routes",
      component: () => import("../pages/RoutePage.vue"),
    },
    {
      path: "/facilities",
      name: "facilities",
      component: () => import("../pages/FacilityPage.vue"),
    },
    {
      path: "/foods",
      name: "foods",
      component: () => import("../pages/FoodPage.vue"),
    },
    {
      path: "/diaries",
      name: "diaries",
      component: () => import("../pages/DiaryPage.vue"),
    },
  ],
});

export default router;
