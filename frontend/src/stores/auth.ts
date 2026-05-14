import { defineStore } from "pinia";

import { api } from "../api/client";
import type { RouteSnapshot, User } from "../types/models";

type AuthMode = "login" | "register";

type ApiFailure = {
  response?: {
    data?: {
      detail?: string;
    };
  };
};

const TOKEN_KEY = "travel_local_token";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    token: localStorage.getItem(TOKEN_KEY) || "",
    user: null as User | null,
    loading: false,
    error: "",
    modalOpen: false,
    modalMode: "login" as AuthMode,
    initialized: false,
  }),
  getters: {
    isLoggedIn: (state) => Boolean(state.token && state.user),
    favoriteDestinationCount: (state) => state.user?.favorite_destination_ids?.length ?? 0,
    favoriteRouteCount: (state) => state.user?.favorite_route_snapshots?.length ?? 0,
  },
  actions: {
    openAuthModal(mode: AuthMode = "login") {
      this.modalMode = mode;
      this.modalOpen = true;
      this.error = "";
    },
    closeAuthModal() {
      this.modalOpen = false;
      this.error = "";
    },
    setSession(token: string, user: User) {
      this.token = token;
      this.user = user;
      localStorage.setItem(TOKEN_KEY, token);
    },
    clearSession() {
      this.token = "";
      this.user = null;
      this.error = "";
      localStorage.removeItem(TOKEN_KEY);
    },
    async restoreSession() {
      if (this.initialized) return;
      this.initialized = true;
      if (!this.token) return;
      try {
        const { data } = await api.get("/auth/me");
        this.user = data.user;
      } catch {
        this.clearSession();
      }
    },
    async login(payload: { username: string; password: string }) {
      this.loading = true;
      this.error = "";
      try {
        const { data } = await api.post("/auth/login", payload);
        this.setSession(data.token, data.user);
        this.closeAuthModal();
      } catch (error: unknown) {
        this.error = (error as ApiFailure)?.response?.data?.detail || "登录失败，请检查账号密码。";
      } finally {
        this.loading = false;
      }
    },
    async register(payload: { username: string; display_name: string; password: string }) {
      this.loading = true;
      this.error = "";
      try {
        const { data } = await api.post("/auth/register", payload);
        this.setSession(data.token, data.user);
        this.closeAuthModal();
      } catch (error: unknown) {
        this.error = (error as ApiFailure)?.response?.data?.detail || "注册失败，请稍后再试。";
      } finally {
        this.loading = false;
      }
    },
    async logout() {
      try {
        await api.post("/auth/logout");
      } finally {
        this.clearSession();
      }
    },
    async toggleDestinationFavorite(sourceId: string) {
      const { data } = await api.post("/auth/favorites/destinations", {
        source_id: sourceId,
      });
      this.user = data.user;
      return data.favorited as boolean;
    },
    async saveRouteFavorite(snapshot: Record<string, unknown> | RouteSnapshot) {
      const { data } = await api.post("/auth/favorites/routes", snapshot);
      this.user = data.user;
    },
    bindUnauthorizedListener() {
      window.addEventListener("travel-auth-cleared", () => {
        this.clearSession();
      });
    },
  },
});
