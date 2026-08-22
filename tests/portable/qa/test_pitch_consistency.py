from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[3]
ROTEIRO = ROOT / "docs" / "pitch" / "roteiro-3-minutos.md"
CANONICAL_AI_DOCS = (
    ROTEIRO,
    ROOT / "docs" / "pitch" / "storyboard.md",
    ROOT / "docs" / "architecture.md",
    ROOT / "docs" / "proposta" / "versao-resumida.md",
    ROOT / "docs" / "proposta" / "versao-tecnica.md",
    ROOT / "docs" / "submission" / "final-form.md",
)


class PitchConsistencyTest(unittest.TestCase):
    def test_spoken_script_fits_three_minutes(self):
        text = ROTEIRO.read_text(encoding="utf-8").split(
            "## Direção do ensaio",
            1,
        )[0]

        spoken = "\n".join(
            line
            for line in text.splitlines()
            if line
            and not line.startswith("#")
            and not line.startswith("Duração-alvo:")
        )

        words = re.findall(
            r"[A-Za-zÀ-ÿ0-9]+(?:[-'][A-Za-zÀ-ÿ0-9]+)?",
            spoken,
        )

        self.assertGreaterEqual(len(words), 350)
        self.assertLessEqual(
            len(words),
            420,
            f"roteiro com {len(words)} palavras",
        )
        self.assertEqual(
            6,
            len(
                re.findall(
                    r"^## Slide \d",
                    text,
                    flags=re.MULTILINE,
                )
            ),
        )

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

    def test_pitch_states_current_controlled_evidence(self):
        text = ROTEIRO.read_text(encoding="utf-8")

        current_evidence = (
            "64 de 64",
            "zero aceites perigosos",
            "65 testes portáteis",
            "36 do bridge",
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
