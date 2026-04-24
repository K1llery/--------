import type { Directive } from "vue";

function handleClick(e: MouseEvent) {
  const el = e.currentTarget as HTMLElement;
  const rect = el.getBoundingClientRect();
  const size = Math.max(rect.width, rect.height);
  const x = e.clientX - rect.left - size / 2;
  const y = e.clientY - rect.top - size / 2;

  const ripple = document.createElement("span");
  ripple.className = "ripple-effect";
  ripple.style.width = ripple.style.height = `${size}px`;
  ripple.style.left = `${x}px`;
  ripple.style.top = `${y}px`;
  el.appendChild(ripple);
  ripple.addEventListener("animationend", () => ripple.remove());
}

export const vRipple: Directive = {
  mounted(el: HTMLElement) {
    el.classList.add("ripple-container");
    el.addEventListener("click", handleClick);
  },
  unmounted(el: HTMLElement) {
    el.removeEventListener("click", handleClick);
  },
};
