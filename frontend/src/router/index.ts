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
      path: "/foods/:id",
      name: "food-detail",
      component: () => import("../pages/FoodDetailPage.vue"),
    },
    {
      path: "/diaries",
      name: "diaries",
      component: () => import("../pages/DiaryPage.vue"),
    },
    {
      path: "/diaries/new",
      name: "diary-new",
      component: () => import("../pages/diaries/DiaryEditorPage.vue"),
    },
    {
      path: "/diaries/me",
      name: "diary-me",
      component: () => import("../pages/diaries/MyDiariesPage.vue"),
    },
    {
      path: "/diaries/:id",
      name: "diary-detail",
      component: () => import("../pages/diaries/DiaryDetailPage.vue"),
    },
    {
      path: "/diaries/:id/edit",
      name: "diary-edit",
      component: () => import("../pages/diaries/DiaryEditorPage.vue"),
    },
    {
      path: "/plan",
      name: "plan",
      component: () => import("../pages/PlanPage.vue"),
    },
  ],
});

export default router;
