"""Автоматические тесты экспертной системы."""

import unittest

from main import analyze_text
from logger import mask_sensitive_data


class ExpertSystemTests(unittest.TestCase):
    def status_for(self, text: str) -> set[str]:
        _, decisions = analyze_text(text, save_log=False)
        return {decision.status for decision in decisions}

    def test_tax_secret_to_competitor(self):
        self.assertIn("НАРУШЕНИЕ", self.status_for("Сотрудник ФНС передал данные о налоговых платежах компании конкуренту."))

    def test_tax_control(self):
        self.assertIn("ЗАКОННО", self.status_for("Компания передала налоговые сведения в ФНС для проведения проверки."))

    def test_audit_with_nda(self):
        self.assertIn("ЗАКОННО", self.status_for("Формула передана внешнему аудитору. Соглашение о конфиденциальности подписано."))

    def test_audit_without_nda(self):
        self.assertIn("ТРЕБУЕТСЯ РУЧНАЯ ПРОВЕРКА", self.status_for("Коммерческая тайна передана для внешнего аудита."))

    def test_due_diligence(self):
        text = "Компания получила коммерческую тайну при due diligence. Сделка не состоялась, но компания использует формулу."
        self.assertIn("НАРУШЕНИЕ", self.status_for(text))

    def test_personal_data_without_consent(self):
        self.assertIn("НАРУШЕНИЕ", self.status_for("Сотрудник передал базу персональных данных клиентов третьему лицу без согласия."))

    def test_personal_data_with_consent(self):
        self.assertIn("ЗАКОННО", self.status_for("Клиент дал письменное согласие на передачу персональных данных третьему лицу."))

    def test_notary_refusal(self):
        text = "Банк отказал нотариусу в данных о счетах умершего клиента, хотя был письменный запрос нотариуса по наследственному делу."
        self.assertIn("НАРУШЕНИЕ", self.status_for(text))

    def test_rosfinmonitoring(self):
        self.assertIn("ЗАКОННО", self.status_for("Банк передал сведения об операциях клиента в Росфинмониторинг."))

    def test_lawyer_oral_authority(self):
        text = "Банк отказал адвокату в выписке по счету клиента, потому что представлена устная доверенность."
        self.assertIn("ЗАКОННО", self.status_for(text))

    def test_medical_secret_to_friend(self):
        self.assertIn("НАРУШЕНИЕ", self.status_for("Санитар по секрету сообщил другу диагноз пациента — ветрянка."))

    def test_police_oral_request(self):
        self.assertIn("НАРУШЕНИЕ", self.status_for("Врач передал полиции данные пациента по устному запросу."))

    def test_foreign_request(self):
        text = "Иностранная налоговая служба запросила налоговые сведения российской компании."
        self.assertIn("ТРЕБУЕТСЯ РУЧНАЯ ПРОВЕРКА", self.status_for(text))

    def test_possible_state_secret(self):
        text = "Я видел пусковую установку и хочу отправить фотографию другу."
        _, decisions = analyze_text(text, save_log=False)
        self.assertTrue(any(item.rule_id == "R19" for item in decisions))

    def test_empty_text(self):
        with self.assertRaises(ValueError):
            analyze_text("   ", save_log=False)

    def test_log_does_not_store_source_text(self):
        source = "Конфиденциальные сведения клиента"
        safe_value = mask_sensitive_data(source)
        self.assertNotIn(source, safe_value)
        self.assertIn("SHA-256", safe_value)


if __name__ == "__main__":
    unittest.main(verbosity=2)
