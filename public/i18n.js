// i18n.js - Internationalization utility
class I18n {
  constructor() {
    this.translations = {};
    this.currentLanguage = this.detectLanguage();
    this.supportedLanguages = ["en", "sl"];
  }

  // Load translations from JSON file
  async load() {
    try {
      const response = await fetch("/i18n.json");
      this.translations = await response.json();
      return true;
    } catch (error) {
      console.error("Failed to load translations:", error);
      return false;
    }
  }

  // Detect browser language or use saved preference
  detectLanguage() {
    // Check localStorage for saved preference
    const saved = localStorage.getItem("language");
    if (saved && this.supportedLanguages.includes(saved)) {
      return saved;
    }

    // Check browser language
    const browserLang = navigator.language.split("-")[0];
    if (this.supportedLanguages.includes(browserLang)) {
      return browserLang;
    }

    // Default to English
    return "en";
  }

  // Set current language and save preference
  setLanguage(lang) {
    if (this.supportedLanguages.includes(lang)) {
      this.currentLanguage = lang;
      localStorage.setItem("language", lang);
      return true;
    }
    return false;
  }

  // Get translation by key path (e.g., 'home.title')
  t(path) {
    const keys = path.split(".");
    let value = this.translations[this.currentLanguage];

    for (const key of keys) {
      if (value && typeof value === "object") {
        value = value[key];
      } else {
        // Fallback to English if translation missing
        value = this.translations["en"];
        for (const k of keys) {
          if (value && typeof value === "object") {
            value = value[k];
          }
        }
        return value || path;
      }
    }

    return value || path;
  }

  // Get current language
  getLanguage() {
    return this.currentLanguage;
  }

  // Get all supported languages
  getLanguages() {
    return this.supportedLanguages;
  }
}

// Create global instance
const i18n = new I18n();

// Initialize on page load
document.addEventListener("DOMContentLoaded", async () => {
  await i18n.load();
  updatePageLanguage();
});

// Update all translatable elements
function updatePageLanguage() {
  document.querySelectorAll("[data-i18n]").forEach((element) => {
    const key = element.getAttribute("data-i18n");
    const translation = i18n.t(key);

    if (element.tagName === "INPUT") {
      // For input placeholders
      const attr = element.getAttribute("data-i18n-attr") || "placeholder";
      element.setAttribute(attr, translation);
    } else if (element.tagName === "TITLE") {
      // For page title
      document.title = translation;
    } else {
      // For text content
      element.textContent = translation;
    }
  });

  // Handle data-i18n-placeholder attributes (for input elements)
  document.querySelectorAll("[data-i18n-placeholder]").forEach((element) => {
    const key = element.getAttribute("data-i18n-placeholder");
    const translation = i18n.t(key);
    element.setAttribute("placeholder", translation);
  });

  // Update language selector if present
  const langSelectors = document.querySelectorAll(".lang-selector");
  langSelectors.forEach((selector) => {
    selector.value = i18n.getLanguage();
  });
}

// Language change handler
function changeLanguage(lang) {
  if (i18n.setLanguage(lang)) {
    updatePageLanguage();
  }
}
