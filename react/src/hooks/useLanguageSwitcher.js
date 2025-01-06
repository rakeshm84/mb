import { useTranslation } from "react-i18next";
import { useMaterialUIController, setDirection } from "context";

const useLanguageSwitcher = () => {
  const [controller, dispatch] = useMaterialUIController();
  const { i18n } = useTranslation();

  const switchLanguage = async (selectedLanguage) => {
    if (!selectedLanguage) {
      selectedLanguage = "en";
    }
    await i18n.changeLanguage(selectedLanguage);

    const isRTL = selectedLanguage === "he"; // Adjust for RTL languages
    const direction = isRTL ? "rtl" : "ltr";

    localStorage.setItem("direction", direction);
    localStorage.setItem("language", selectedLanguage);
    setDirection(dispatch, direction);
    document.documentElement.dir = direction;
  };

  const getActiveLang = () => {
    return localStorage.getItem("language");
  };

  return { switchLanguage, getActiveLang };
};

export default useLanguageSwitcher;
