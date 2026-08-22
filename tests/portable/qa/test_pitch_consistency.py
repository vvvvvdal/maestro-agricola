from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
STORYBOARD = ROOT / "docs" / "pitch" / "storyboard.md"
CANONICAL_AI_DOCS = (
    STORYBOARD,
    ROOT / "docs" / "architecture.md",
    ROOT / "docs" / "proposta" / "versao-resumida.md",
    ROOT / "docs" / "proposta" / "versao-tecnica.md",
    ROOT / "docs" / "submission" / "final-form.md",
)


class PitchConsistencyTest(unittest.TestCase):
    def test_canonical_docs_do_not_restore_old_model_numbers(self):
        obsolete = (
            "96 frases",
            "65 KB",
            "15 de 16",
            "15/16",
        )

        for path in CANONICAL_AI_DOCS:
            text = path.read_text(encoding="utf-8")

            for phrase in obsolete:
                with self.subTest(
                    path=path.name,
                    phrase=phrase,
                ):
                    self.assertNotIn(
                        phrase,
                        text,
                    )

    def test_pitch_materials_state_current_controlled_evidence(self):
        text = STORYBOARD.read_text(encoding="utf-8")

        current_evidence = (
            "64/64",
            "zero aceite perigoso",
            "65 + 36 testes",
            "MockDeviceKit",
            "pré-hardware",
        )

        for fact in current_evidence:
            with self.subTest(fact=fact):
                self.assertIn(
                    fact,
                    text,
                )


if __name__ == "__main__":
    unittest.main()
