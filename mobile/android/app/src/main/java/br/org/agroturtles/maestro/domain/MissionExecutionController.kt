package br.org.agroturtles.maestro.domain

import java.time.Clock
import java.time.Instant
import java.util.UUID

enum class MissionExecutionState {
    REVIEW,
    AWAITING_CONFIRMATION,
    AWAITING_QUERY,
    AWAITING_OPERATION,
    PAUSED,
    COMPLETED,
    CANCELLED,
}

data class MissionExecutionSnapshot(
    val plan: MissionPlan,
    val state: MissionExecutionState,
    val currentStepIndex: Int,
    val reason: String? = null,
) {
    val currentStep: MissionStep? get() = plan.steps.getOrNull(currentStepIndex)
}

sealed interface MissionExecutionAction {
    data class AwaitingConfirmation(val step: MissionStep) : MissionExecutionAction
    data class ExecuteQuery(val step: MissionStep) : MissionExecutionAction
    data class SendCommand(val command: Command, val step: MissionStep) : MissionExecutionAction
    data class Paused(val reason: String) : MissionExecutionAction
    data object Completed : MissionExecutionAction
    data object Cancelled : MissionExecutionAction
}

/**
 * Executes the typed plan one step at a time. It never receives free-form
 * language and never sends a ROS payload: the app transports only the existing
 * validated Command generated after each individual voice confirmation.
 */
class MissionExecutionController(
    private val targetResolver: TargetResolver,
    private val clock: Clock = Clock.systemUTC(),
    private val commandIdFactory: () -> String = { UUID.randomUUID().toString() },
) {
    private var snapshot: MissionExecutionSnapshot? = null

    fun begin(plan: MissionPlan): MissionExecutionAction {
        val invalid = validate(plan)
        if (invalid != null) {
            snapshot = MissionExecutionSnapshot(plan, MissionExecutionState.PAUSED, 0, invalid)
            return MissionExecutionAction.Paused(invalid)
        }
        snapshot = MissionExecutionSnapshot(plan, MissionExecutionState.REVIEW, 0)
        return advance()
    }

    fun current(): MissionExecutionSnapshot? = snapshot

    fun confirm(prediction: IntentPrediction): MissionExecutionAction {
        val current = requireState(MissionExecutionState.AWAITING_CONFIRMATION) ?: return paused(
            "Não há ação física aguardando confirmação."
        )
        val step = checkNotNull(current.currentStep)
        return when (prediction.label) {
            "CONFIRM" -> {
                val command = Command(
                    commandId = commandIdFactory(),
                    createdAt = Instant.now(clock).toString(),
                    intent = step.intent.name,
                    targetId = step.targetId,
                )
                snapshot = current.copy(state = MissionExecutionState.AWAITING_OPERATION)
                MissionExecutionAction.SendCommand(command, step)
            }

            "CANCEL" -> cancel()
            else -> MissionExecutionAction.AwaitingConfirmation(step)
        }
    }

    fun commandRejected(reason: String): MissionExecutionAction = paused(
        "O robô recusou a etapa atual: $reason."
    )

    fun operationFinished(succeeded: Boolean, reason: String): MissionExecutionAction {
        val current = requireState(MissionExecutionState.AWAITING_OPERATION) ?: return paused(
            "Não há operação da missão em acompanhamento."
        )
        if (!succeeded) return paused(reason)
        snapshot = current.copy(currentStepIndex = current.currentStepIndex + 1)
        return advance()
    }

    fun queryFinished(succeeded: Boolean, reason: String): MissionExecutionAction {
        val current = requireState(MissionExecutionState.AWAITING_QUERY) ?: return paused(
            "Não há consulta da missão em acompanhamento."
        )
        if (!succeeded) return paused(reason)
        snapshot = current.copy(currentStepIndex = current.currentStepIndex + 1)
        return advance()
    }

    fun confirmationTimedOut(): MissionExecutionAction = paused(
        "A confirmação da etapa expirou."
    )

    fun cancel(): MissionExecutionAction {
        val current = snapshot ?: return MissionExecutionAction.Cancelled
        snapshot = current.copy(state = MissionExecutionState.CANCELLED)
        return MissionExecutionAction.Cancelled
    }

    private fun advance(): MissionExecutionAction {
        val current = checkNotNull(snapshot)
        val step = current.currentStep
        if (step == null) {
            snapshot = current.copy(state = MissionExecutionState.COMPLETED)
            return MissionExecutionAction.Completed
        }
        return when (step.intent) {
            MissionStepIntent.PLOT_STATUS_QUERY -> {
                snapshot = current.copy(state = MissionExecutionState.AWAITING_QUERY)
                MissionExecutionAction.ExecuteQuery(step)
            }

            MissionStepIntent.UNDOCK,
            MissionStepIntent.SPRAY,
            MissionStepIntent.DOCK -> {
                snapshot = current.copy(state = MissionExecutionState.AWAITING_CONFIRMATION)
                MissionExecutionAction.AwaitingConfirmation(step)
            }
        }
    }

    private fun paused(reason: String): MissionExecutionAction {
        val current = snapshot ?: return MissionExecutionAction.Paused(reason)
        snapshot = current.copy(state = MissionExecutionState.PAUSED, reason = reason)
        return MissionExecutionAction.Paused(reason)
    }

    private fun requireState(expected: MissionExecutionState): MissionExecutionSnapshot? =
        snapshot?.takeIf { it.state == expected }

    private fun validate(plan: MissionPlan): String? {
        if (plan.schemaVersion != "1.0") return "Versão do plano não suportada."
        if (plan.steps.size !in 2..4) return "A missão precisa ter entre duas e quatro etapas."
        if (plan.steps.map(MissionStep::stepId).distinct().size != plan.steps.size) {
            return "A missão tem etapas repetidas."
        }
        plan.steps.forEach { step ->
            val targetRequired = step.intent == MissionStepIntent.SPRAY ||
                step.intent == MissionStepIntent.PLOT_STATUS_QUERY
            if (targetRequired && !isMappedTarget(step.targetId)) {
                return "O alvo da etapa ${step.stepId} não é um talhão mapeado."
            }
            if (!targetRequired && step.targetId != null) {
                return "A etapa ${step.stepId} não aceita alvo."
            }
        }
        val undock = plan.steps.indexOfFirst { it.intent == MissionStepIntent.UNDOCK }
        if (undock > 0) return "Sair da doca precisa ser a primeira etapa."
        val dock = plan.steps.indexOfFirst { it.intent == MissionStepIntent.DOCK }
        if (dock >= 0 && dock != plan.steps.lastIndex) {
            return "Voltar para a doca precisa ser a última etapa."
        }
        return null
    }

    private fun isMappedTarget(targetId: String?): Boolean =
        targetResolver.resolve(null, targetId.orEmpty()).status == TargetResolutionStatus.RESOLVED
}
