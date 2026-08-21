package br.org.agroturtles.maestro.domain


/**
 * Human readable names shared pelo texto da tela e pelas mensagens de voz.
 *
 * O identificador tecnico (`plot-03`) continua sendo o valor do contrato; estes
 * rotulos existem apenas para apresentacao e para o TTS em pt-BR, que le
 * "plot-03" de forma pouco natural.
 */

private val PLOT_NUMBER = Regex("[0-9]+")

fun plotLabel(targetId: String?): String {
    if (targetId.isNullOrBlank()) return "alvo desconhecido"
    val number = PLOT_NUMBER.find(targetId)?.value?.toIntOrNull() ?: return targetId
    return "talhão $number"
}

fun actionLabel(intent: String?): String = when (intent) {
    "SPRAY" -> "Pulverizar"
    "DOCK" -> "Retornar à doca"
    "UNDOCK" -> "Sair da doca"
    "CONFIRM" -> "Confirmar"
    "CANCEL" -> "Cancelar"
    else -> "Ação não reconhecida"
}
