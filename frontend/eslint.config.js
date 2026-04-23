import js from "@eslint/js";
import tseslint from "typescript-eslint";
import pluginVue from "eslint-plugin-vue";
import vueParser from "vue-eslint-parser";
import globals from "globals";
import prettierConfig from "eslint-config-prettier";

export default [
  { ignores: ["dist/**", "node_modules/**"] },

  {
    files: ["src/**/*.ts", "src/**/*.vue"],
    languageOptions: {
      globals: {
        ...globals.browser,
      },
    },
  },

  js.configs.recommended,

  ...tseslint.configs.recommended.map((config) => ({
    ...config,
    files: ["src/**/*.ts", "src/**/*.vue"],
  })),

  ...pluginVue.configs["flat/recommended"].map((config) => ({
    ...config,
    files: ["src/**/*.vue"],
  })),

  {
    files: ["src/**/*.vue"],
    languageOptions: {
      parser: vueParser,
      parserOptions: {
        parser: tseslint.parser,
        project: null,
        ecmaVersion: "latest",
        sourceType: "module",
      },
    },
  },

  {
    files: ["src/**/*.ts"],
    languageOptions: {
      parser: tseslint.parser,
      parserOptions: {
        project: null,
        ecmaVersion: "latest",
        sourceType: "module",
      },
    },
  },

  {
    files: ["src/**/*.ts", "src/**/*.vue"],
    rules: {
      "vue/multi-word-component-names": "off",
      "vue/attributes-order": "off",
      "no-undef": "off",
      "@typescript-eslint/no-explicit-any": "warn",
      "@typescript-eslint/no-unused-vars": [
        "warn",
        { argsIgnorePattern: "^_", caughtErrors: "none", varsIgnorePattern: "^(IndoorRouteResult|MultiRouteResult|SingleRouteResult)$" },
      ],
      "@typescript-eslint/no-empty-object-type": "off",
    },
  },

  prettierConfig,
];
