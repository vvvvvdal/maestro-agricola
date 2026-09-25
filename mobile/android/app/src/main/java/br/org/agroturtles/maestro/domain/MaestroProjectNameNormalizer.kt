package br.org.agroturtles.maestro.domain

/** Repairs common ASR variants of the project name before local Qwen receives an UNKNOWN turn. */
object MaestroProjectNameNormalizer {
    private val projectNameVariants = Regex(
        """\b(?:uma\s+|um\s+|a\s+|o\s+)?(?:extra|mestre|mestra|maestra)\s+agr[ií]col[ao]\b""",
        RegexOption.IGNORE_CASE,
    )

    fun normalizeForAssistant(text: String): String =
        projectNameVariants.replace(text, "o Maestro Agrícola")
}
