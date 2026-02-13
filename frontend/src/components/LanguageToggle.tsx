import { ToggleButton, ToggleButtonGroup, Tooltip } from "@mui/material";
import { useTranslation } from "react-i18next";

export default function LanguageToggle() {
  const { i18n, t } = useTranslation();
  const current = i18n.language.startsWith("de") ? "de" : "en";

  return (
    <Tooltip title={`${t("langShort.de")} / ${t("langShort.en")}`}>
      <ToggleButtonGroup
        size="small"
        exclusive
        value={current}
        onChange={(_, value) => {
          if (value) void i18n.changeLanguage(value);
        }}
        aria-label="language switch"
      >
        <ToggleButton value="de">{t("langShort.de")}</ToggleButton>
        <ToggleButton value="en">{t("langShort.en")}</ToggleButton>
      </ToggleButtonGroup>
    </Tooltip>
  );
}
