import type { Directive } from "vue";

const observer = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        const el = entry.target as HTMLElement;
        const delay = el.dataset.revealDelay || "0";
        setTimeout(() => el.classList.add("is-visible"), Number(delay));
        observer.unobserve(el);
      }
    });
  },
  { threshold: 0.08, rootMargin: "0px 0px -40px 0px" },
);

export const vReveal: Directive = {
  mounted(el: HTMLElement, binding) {
    el.classList.add("v-reveal");
    if (typeof binding.value === "number") {
      el.dataset.revealDelay = String(binding.value);
    }
    observer.observe(el);
  },
  unmounted(el: HTMLElement) {
    observer.unobserve(el);
  },
};
