package br.org.agroturtles.maestro

import android.Manifest
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import kotlinx.coroutines.delay
import br.org.agroturtles.maestro.domain.InteractionEngine
import br.org.agroturtles.maestro.domain.InteractionResult
import br.org.agroturtles.maestro.domain.InteractionState
import br.org.agroturtles.maestro.domain.IntentPrediction
import br.org.agroturtles.maestro.domain.Command
import br.org.agroturtles.maestro.domain.JevIntentClassifier
import br.org.agroturtles.maestro.domain.LanguageDispatch
import br.org.agroturtles.maestro.domain.LanguageInteractionController
import br.org.agroturtles.maestro.domain.LocalIntentClassifier
import br.org.agroturtles.maestro.domain.MissionPlan
import br.org.agroturtles.maestro.domain.MissionExecutionAction
import br.org.agroturtles.maestro.domain.MissionExecutionController
import br.org.agroturtles.maestro.domain.MissionExecutionSnapshot
import br.org.agroturtles.maestro.domain.MissionExecutionState
import br.org.agroturtles.maestro.domain.MissionPreviewParseResult
import br.org.agroturtles.maestro.domain.MissionPreviewParser
import br.org.agroturtles.maestro.domain.MissionStep
import br.org.agroturtles.maestro.domain.MissionStepIntent
import br.org.agroturtles.maestro.domain.PlotStatusQueryController
import br.org.agroturtles.maestro.domain.QwenDomainAssistant
import br.org.agroturtles.maestro.domain.RemoteTranscriptBlockReason
import br.org.agroturtles.maestro.domain.RemoteTranscriptDecision
import br.org.agroturtles.maestro.domain.RemoteTranscriptGate
import br.org.agroturtles.maestro.domain.ReadOnlyLanguageRoute
import br.org.agroturtles.maestro.domain.ReadOnlyLanguageRouter
import br.org.agroturtles.maestro.domain.RobotStatusQueryController
import br.org.agroturtles.maestro.domain.TargetResolver
import br.org.agroturtles.maestro.platform.NativeQwenEngine
import br.org.agroturtles.maestro.platform.PlatformFrameSource
import br.org.agroturtles.maestro.platform.VoiceIO
import br.org.agroturtles.maestro.platform.WebSocketCommandTransport
import br.org.agroturtles.maestro.platform.WebSocketReadOnlyQueryTransport
import br.org.agroturtles.maestro.platform.JevProxyChoiceEvaluator
import br.org.agroturtles.maestro.ui.MaestroScreen
import br.org.agroturtles.maestro.ui.MaestroTheme
import br.org.agroturtles.maestro.ui.UnknownRobotPresentation
import br.org.agroturtles.maestro.ui.robotPresentation
import java.io.File
import java.util.concurrent.Executors
import java.util.concurrent.atomic.AtomicLong


private const val DEFAULT_ENDPOINT = "ws://10.0.2.2:18765"
private const val TEST_SETTINGS = "maestro_test_settings"
private const val ENDPOINT_PREFERENCE = "bridge_endpoint"
private const val OPERATION_STATUS_MAX_POLLS = 60
private const val QWEN_MODEL_FILENAME = "qwen2.5-1.5b-q4_k_m.gguf"
private const val ASSISTANT_PROCESSING_MESSAGE = "Processando resposta local…"
private const val ASSISTANT_ERROR_MESSAGE =
    "Assistente local indisponível. Nada foi enviado ao robô."
private const val MISSION_PREVIEW_TIMEOUT_MILLIS = 60_000L


class MainActivity : ComponentActivity() {
    private lateinit var voice: VoiceIO
    private lateinit var frameSource: PlatformFrameSource
    private var qwenEngine: NativeQwenEngine? = null
    private var languageController: LanguageInteractionController? = null
    private val jevExecutor = Executors.newSingleThreadExecutor()
    private val jevRequest = AtomicLong(0)
    private val operationRequest = AtomicLong(0)
    private val inspectionRequest = AtomicLong(0)
    private val uiHandler = Handler(Looper.getMainLooper())
    private var onMicrophoneGranted: (() -> Unit)? = null
    private val microphonePermission = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { granted ->
        if (granted) onMicrophoneGranted?.invoke()
        onMicrophoneGranted = null
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        voice = VoiceIO(this)
        val modelJson = assets.open("intent_model.json").bufferedReader().use { it.readText() }
        val targetMapJson = assets.open("targets.json").bufferedReader().use { it.readText() }
        val classifier = LocalIntentClassifier.fromJson(modelJson)
        val jevEvaluator = JevProxyChoiceEvaluator()
        val jevClassifier = JevIntentClassifier(jevEvaluator)
        val targetResolver = TargetResolver.fromJson(targetMapJson)
        val missionPreviewParser = MissionPreviewParser(targetResolver)
        val missionExecutionController = MissionExecutionController(targetResolver)
        val engine = InteractionEngine(
            classifier,
            targetResolver,
        )
        val qwenModel = File(filesDir, QWEN_MODEL_FILENAME)
        val assistant = qwenModel
            .takeIf(File::isFile)
            ?.let { modelFile ->
                NativeQwenEngine(modelFile.absolutePath)
                    .also { qwenEngine = it }
            }
            ?.let(::QwenDomainAssistant)
        val language = LanguageInteractionController(
            classifier = classifier,
            interactionEngine = engine,
            assistant = assistant,
        )
        languageController = language
        frameSource = PlatformFrameSource(this, targetMapJson)
        val testSettings = getSharedPreferences(TEST_SETTINGS, MODE_PRIVATE)
        val savedEndpoint = testSettings.getString(ENDPOINT_PREFERENCE, DEFAULT_ENDPOINT)
            ?: DEFAULT_ENDPOINT
        setContent {
            var result by remember { mutableStateOf(engine.reset()) }
            var transcript by remember { mutableStateOf("") }
            var endpoint by remember { mutableStateOf(savedEndpoint) }
            var robot by remember { mutableStateOf(UnknownRobotPresentation) }
            var secondsToExpire by remember { mutableIntStateOf(0) }
            var jevRemoteEnabled by remember { mutableStateOf(false) }
            var jevRemoteConsent by remember { mutableStateOf(false) }
            var jevPending by remember { mutableStateOf(false) }
            var readOnlyPending by remember { mutableStateOf(false) }
            var operationTracking by remember { mutableStateOf<Command?>(null) }
            var operationSafetyHold by remember { mutableStateOf(false) }
            var inspectionPending by remember { mutableStateOf(false) }
            var remoteSessionConsentPrompt by remember { mutableStateOf(false) }
            var remoteBlockReason by remember { mutableStateOf<RemoteTranscriptBlockReason?>(null) }
            var missionPreview by remember { mutableStateOf<MissionPlan?>(null) }
            var missionExecution by remember { mutableStateOf<MissionExecutionSnapshot?>(null) }
            val readOnlyRequest = remember { AtomicLong(0) }
            val readOnlyLanguageRouter = remember { ReadOnlyLanguageRouter() }
            val plotStatusQueries = remember(endpoint) {
                PlotStatusQueryController(
                    targetResolver = targetResolver,
                    transportFactory = { WebSocketReadOnlyQueryTransport(endpoint) },
                    languageRouter = readOnlyLanguageRouter,
                )
            }
            val robotStatusQueries = remember(endpoint) {
                RobotStatusQueryController(
                    transportFactory = { WebSocketReadOnlyQueryTransport(endpoint) },
                    languageRouter = readOnlyLanguageRouter,
                )
            }

            fun trackAcceptedOperation(
                command: Command,
                onTerminal: ((InteractionResult) -> Unit)? = null,
            ) {
                val requestId = operationRequest.incrementAndGet()
                operationTracking = command
                result = robotStatusQueries.trackingStarted(command)
                var pollsRemaining = OPERATION_STATUS_MAX_POLLS

                fun poll() {
                    if (pollsRemaining-- <= 0) {
                        if (
                            operationRequest.get() == requestId &&
                            operationTracking?.commandId == command.commandId
                        ) {
                            val timedOut = robotStatusQueries.trackingTimedOut(command).result
                            result = timedOut
                            operationTracking = null
                            if (onTerminal == null) {
                                operationSafetyHold = true
                            } else {
                                onTerminal(timedOut)
                            }
                        }
                        return
                    }
                    robotStatusQueries.track(command) { update ->
                        runOnUiThread {
                            if (
                                operationRequest.get() != requestId ||
                                operationTracking?.commandId != command.commandId
                            ) {
                                return@runOnUiThread
                            }
                            result = update.result
                            update.result.speech?.let(voice::speak)
                            if (update.terminal) {
                                operationTracking = null
                                onTerminal?.invoke(update.result)
                            } else {
                                uiHandler.postDelayed({ poll() }, 1_000)
                            }
                        }
                    }
                }

                poll()
            }

            fun apply(next: InteractionResult) {
                result = next
                if (next.state == InteractionState.ACCEPTED && next.command != null) {
                    robot = robotPresentation(next.intent, next.targetId)
                }
                next.speech?.let(voice::speak)
                next.command?.let { command ->
                    WebSocketCommandTransport(endpoint).send(command) { accepted, reason ->
                        runOnUiThread {
                            apply(engine.transportCompleted(accepted, reason))
                            if (accepted) trackAcceptedOperation(command)
                        }
                    }
                }
            }

            fun missionStepName(step: MissionStep): String = when (step.intent) {
                MissionStepIntent.UNDOCK -> "sair da doca"
                MissionStepIntent.SPRAY -> "pulverizar ${step.targetId}"
                MissionStepIntent.PLOT_STATUS_QUERY -> "consultar o histórico de ${step.targetId}"
                MissionStepIntent.DOCK -> "voltar para a doca"
            }

            fun applyMission(next: InteractionResult, onSpeechFinished: (() -> Unit)? = null) {
                result = next
                next.speech?.let { voice.speak(it, onSpeechFinished) }
            }

            fun executeMissionAction(action: MissionExecutionAction) {
                missionExecution = missionExecutionController.current()
                when (action) {
                    is MissionExecutionAction.AwaitingConfirmation -> {
                        val current = checkNotNull(missionExecution)
                        val name = missionStepName(action.step)
                        applyMission(
                            InteractionResult(
                                state = InteractionState.AWAITING_CONFIRMATION,
                                message = "Etapa ${current.currentStepIndex + 1}: $name?",
                                speech = "Etapa ${current.currentStepIndex + 1} da missão: $name. Confirmar?",
                                intent = "MISSION_PREVIEW",
                            )
                        )
                    }

                    is MissionExecutionAction.ExecuteQuery -> {
                        readOnlyPending = true
                        val targetId = checkNotNull(action.step.targetId)
                        val pending = plotStatusQueries.queryPlot(targetId) { succeeded, queryResult ->
                            runOnUiThread {
                                readOnlyPending = false
                                val next = missionExecutionController.queryFinished(
                                    succeeded,
                                    queryResult.message,
                                )
                                if (succeeded) {
                                    applyMission(queryResult) {
                                        if (missionPreview != null) {
                                            executeMissionAction(next)
                                        }
                                    }
                                } else {
                                    executeMissionAction(next)
                                }
                            }
                        }
                        applyMission(pending)
                    }

                    is MissionExecutionAction.SendCommand -> {
                        applyMission(
                            InteractionResult(
                                state = InteractionState.SENDING,
                                message = "Enviando etapa da missão: ${missionStepName(action.step)}.",
                                intent = "MISSION_PREVIEW",
                            )
                        )
                        WebSocketCommandTransport(endpoint).send(action.command) { accepted, reason ->
                            runOnUiThread {
                                if (!accepted) {
                                    executeMissionAction(missionExecutionController.commandRejected(reason))
                                    return@runOnUiThread
                                }
                                robot = robotPresentation(action.command.intent, action.command.targetId)
                                trackAcceptedOperation(action.command) { terminal ->
                                    executeMissionAction(
                                        missionExecutionController.operationFinished(
                                            succeeded = terminal.state == InteractionState.COMPLETED,
                                            reason = terminal.message,
                                        )
                                    )
                                }
                            }
                        }
                    }

                    is MissionExecutionAction.Paused -> {
                        applyMission(
                            InteractionResult(
                                state = InteractionState.OPERATION_FAILED,
                                message = "Missão pausada: ${action.reason}",
                                speech = "Missão pausada. ${action.reason} Nenhuma etapa seguinte foi enviada.",
                                intent = "MISSION_PREVIEW",
                            )
                        )
                    }

                    MissionExecutionAction.Completed -> {
                        missionPreview = null
                        missionExecution = null
                        applyMission(
                            InteractionResult(
                                state = InteractionState.COMPLETED,
                                message = "Missão concluída no Gazebo.",
                                speech = "Missão concluída no Gazebo.",
                                intent = "MISSION_PREVIEW",
                            )
                        )
                    }

                    MissionExecutionAction.Cancelled -> {
                        missionPreview = null
                        missionExecution = null
                        apply(engine.missionPreviewCancelled())
                    }
                }
            }

            fun handleMissionPrediction(prediction: IntentPrediction) {
                executeMissionAction(missionExecutionController.confirm(prediction))
            }

            fun applyDispatch(dispatch: LanguageDispatch) {
                when (dispatch) {
                    is LanguageDispatch.Operational -> apply(dispatch.result)
                    is LanguageDispatch.AssistantPending -> {
                        result = result.copy(
                            message = ASSISTANT_PROCESSING_MESSAGE,
                            speech = null,
                            command = null,
                            prediction = dispatch.prediction,
                        )
                    }
                }
            }

            fun classifyRemotely(text: String) {
                val requestId = jevRequest.incrementAndGet()
                jevPending = true
                result = result.copy(
                    message = "Classificando com Jev remoto",
                    speech = null,
                    command = null,
                )
                jevExecutor.execute {
                    val prediction = jevClassifier.classify(text)
                    runOnUiThread {
                        if (jevRequest.get() == requestId) {
                            jevPending = false
                            if (missionExecution?.state == MissionExecutionState.AWAITING_CONFIRMATION) {
                                handleMissionPrediction(prediction)
                                return@runOnUiThread
                            }
                            applyDispatch(
                                language.handlePrediction(text, prediction) { prediction, outcome ->
                                    runOnUiThread {
                                        outcome.fold(
                                            onSuccess = { reply ->
                                                apply(
                                                    result.copy(
                                                        message = reply.response,
                                                        speech = reply.response,
                                                        command = null,
                                                        prediction = prediction,
                                                    )
                                                )
                                            },
                                            onFailure = {
                                                apply(
                                                    result.copy(
                                                        message = ASSISTANT_ERROR_MESSAGE,
                                                        speech = ASSISTANT_ERROR_MESSAGE,
                                                        command = null,
                                                        prediction = prediction,
                                                    )
                                                )
                                            },
                                        )
                                    }
                                }
                            )
                        }
                    }
                }
            }

            fun interpretLocally(text: String) {

                val dispatch = language.handle(text) { prediction, outcome ->
                    runOnUiThread {
                        outcome.fold(
                            onSuccess = { reply ->
                                apply(
                                    result.copy(
                                        message = reply.response,
                                        speech = reply.response,
                                        command = null,
                                        prediction = prediction,
                                    )
                                )
                            },
                            onFailure = {
                                apply(
                                    result.copy(
                                        message = ASSISTANT_ERROR_MESSAGE,
                                        speech = ASSISTANT_ERROR_MESSAGE,
                                        command = null,
                                        prediction = prediction,
                                    )
                                )
                            },
                        )
                    }
                }

                applyDispatch(dispatch)
            }

            fun inspectMarker() {
                val requestId = inspectionRequest.incrementAndGet()
                inspectionPending = true
                jevRequest.incrementAndGet()
                jevPending = false
                language.cancelAssistant()
                apply(engine.inspectionStarted())
                frameSource.captureTarget { outcome ->
                    runOnUiThread {
                        if (inspectionRequest.get() != requestId) return@runOnUiThread
                        inspectionPending = false
                        outcome
                            .onSuccess { apply(engine.inspectionCompleted(it.targetId)) }
                            .onFailure {
                                apply(engine.targetCaptureFailed(
                                    it.message ?: "Falha ao capturar o alvo"
                                ))
                            }
                    }
                }
            }

            fun interpret(text: String) {
                if (jevPending || readOnlyPending || operationTracking != null) return
                if (missionExecution?.state == MissionExecutionState.AWAITING_CONFIRMATION) {
                    if (jevRemoteEnabled && BuildConfig.FRAME_SOURCE == "mock") {
                        when (val decision = RemoteTranscriptGate.evaluate(text)) {
                            RemoteTranscriptDecision.Allowed -> {
                                transcript = ""
                                classifyRemotely(text)
                            }
                            is RemoteTranscriptDecision.Blocked -> {
                                transcript = ""
                                remoteBlockReason = decision.reason
                            }
                        }
                    } else {
                        handleMissionPrediction(classifier.classify(text))
                    }
                    return
                }
                if (missionPreview != null) return
                if (engine.state in setOf(InteractionState.IDLE, InteractionState.TARGET_READY)) {
                    when (val missionResult = missionPreviewParser.parse(text)) {
                        MissionPreviewParseResult.NotApplicable -> Unit
                        is MissionPreviewParseResult.Preview -> {
                            transcript = ""
                            missionPreview = missionResult.plan
                            apply(engine.missionPreviewed(missionResult.plan.steps.size))
                            return
                        }

                        is MissionPreviewParseResult.Rejected -> {
                            transcript = ""
                            apply(engine.missionPreviewRejected(missionResult.reason))
                            return
                        }
                    }
                    if (readOnlyLanguageRouter.route(text) == ReadOnlyLanguageRoute.INSPECT_TARGET) {
                        inspectMarker()
                        return
                    }
                    val requestId = readOnlyRequest.incrementAndGet()
                    val queryResult = plotStatusQueries.handle(text) { response ->
                        runOnUiThread {
                            if (readOnlyRequest.get() == requestId) {
                                readOnlyPending = false
                                apply(response)
                            }
                        }
                    }
                    if (queryResult != null) {
                        readOnlyPending = queryResult.state == InteractionState.QUERYING
                        apply(queryResult)
                        return
                    }
                    val statusResult = robotStatusQueries.handle(text) { response ->
                        runOnUiThread {
                            if (readOnlyRequest.get() == requestId) {
                                readOnlyPending = false
                                apply(response)
                            }
                        }
                    }
                    if (statusResult != null) {
                        readOnlyPending = statusResult.state == InteractionState.QUERYING
                        apply(statusResult)
                        return
                    }
                }
                if (jevRemoteEnabled && BuildConfig.FRAME_SOURCE == "mock") {
                    when (val decision = RemoteTranscriptGate.evaluate(text)) {
                        RemoteTranscriptDecision.Allowed -> {
                            transcript = ""
                            classifyRemotely(text)
                        }
                        is RemoteTranscriptDecision.Blocked -> {
                            transcript = ""
                            remoteBlockReason = decision.reason
                            apply(
                                engine.reset().copy(
                                    message = "Fala descartada localmente. Nenhum dado foi enviado ao Jev.",
                                    speech = null,
                                )
                            )
                        }
                    }
                    return
                }

                interpretLocally(text)
            }

            LaunchedEffect(result.state) {
                if (result.state != InteractionState.AWAITING_CONFIRMATION) {
                    secondsToExpire = 0
                    return@LaunchedEffect
                }
                for (second in InteractionEngine.CONFIRMATION_TIMEOUT_SECONDS downTo 1) {
                    secondsToExpire = second
                    delay(1_000)
                }
                secondsToExpire = 0
                if (missionExecution?.state == MissionExecutionState.AWAITING_CONFIRMATION) {
                    executeMissionAction(missionExecutionController.confirmationTimedOut())
                } else {
                    apply(engine.confirmationTimedOut())
                }
            }

            LaunchedEffect(missionPreview?.planId, missionExecution?.state) {
                val currentPlan = missionPreview ?: return@LaunchedEffect
                val currentState = missionExecution?.state
                if (currentState != null && currentState != MissionExecutionState.REVIEW) {
                    return@LaunchedEffect
                }
                delay(MISSION_PREVIEW_TIMEOUT_MILLIS)
                if (
                    missionPreview?.planId == currentPlan.planId &&
                    (missionExecution == null || missionExecution?.state == MissionExecutionState.REVIEW)
                ) {
                    missionPreview = null
                    apply(engine.missionPreviewCancelled(expired = true))
                }
            }

            MaestroTheme {
                val missionBlocksInput = missionPreview != null &&
                    missionExecution?.state != MissionExecutionState.AWAITING_CONFIRMATION
                MaestroScreen(
                    result = result,
                    robot = robot,
                    frameSource = BuildConfig.FRAME_SOURCE,
                    jevRemoteEnabled = jevRemoteEnabled,
                    jevRemoteConsent = jevRemoteConsent,
                    onJevRemoteEnabledChange = { enabled ->
                        jevRequest.incrementAndGet()
                        jevPending = false
                        jevRemoteEnabled = enabled && BuildConfig.FRAME_SOURCE == "mock"
                        jevEvaluator.enabled = jevRemoteEnabled
                    },
                    onJevRemoteConsentChange = { consent ->
                        if (consent) {
                            remoteSessionConsentPrompt = true
                        } else {
                            remoteSessionConsentPrompt = false
                            jevRemoteConsent = false
                            jevRequest.incrementAndGet()
                            jevPending = false
                            jevRemoteEnabled = false
                            jevEvaluator.enabled = false
                        }
                    },
                    endpoint = endpoint,
                    onEndpointChange = {
                        endpoint = it
                        testSettings.edit().putString(ENDPOINT_PREFERENCE, it).apply()
                    },
                    transcript = transcript,
                    onTranscriptChange = { transcript = it },
                    secondsToExpire = secondsToExpire,
                    interactionPending = jevPending || readOnlyPending || operationTracking != null || operationSafetyHold || inspectionPending || missionBlocksInput,
                    resetEnabled = !jevPending && !readOnlyPending && operationTracking == null && missionPreview == null,
                    missionPreview = missionPreview,
                    missionExecution = missionExecution,
                    remoteSessionConsentPrompt = remoteSessionConsentPrompt,
                    remoteBlockReason = remoteBlockReason,
                    onConfirmRemoteSession = {
                        remoteSessionConsentPrompt = false
                        jevRemoteConsent = true
                    },
                    onDismissRemoteSession = { remoteSessionConsentPrompt = false },
                    onDismissRemoteBlock = { remoteBlockReason = null },
                    onLook = ::inspectMarker,
                    onListen = {
                        jevRequest.incrementAndGet()
                        jevPending = false
                        language.cancelAssistant()
                        onMicrophoneGranted = {
                            voice.listen { outcome ->
                                runOnUiThread {
                                    outcome.onSuccess {
                                        transcript = it
                                        interpret(it)
                                    }
                                    outcome.onFailure {
                                        apply(
                                            engine.reset().copy(
                                                message = it.message ?: "Falha de voz",
                                            )
                                        )
                                    }
                                }
                            }
                        }
                        microphonePermission.launch(Manifest.permission.RECORD_AUDIO)
                    },
                    onInterpret = { interpret(transcript) },
                    onStartMission = {
                        missionPreview?.let { plan ->
                            executeMissionAction(missionExecutionController.begin(plan))
                        }
                    },
                    onCancelMissionPreview = {
                        executeMissionAction(missionExecutionController.cancel())
                    },
                    onReset = {
                        jevRequest.incrementAndGet()
                        jevPending = false
                        readOnlyRequest.incrementAndGet()
                        readOnlyPending = false
                        operationRequest.incrementAndGet()
                        operationTracking = null
                        operationSafetyHold = false
                        inspectionRequest.incrementAndGet()
                        inspectionPending = false
                        remoteSessionConsentPrompt = false
                        remoteBlockReason = null
                        missionPreview = null
                        missionExecution = null
                        language.cancelAssistant()
                        frameSource.cancelCapture()
                        apply(engine.reset())
                    },
                )
            }
        }
    }

    override fun onDestroy() {
        languageController?.cancelAssistant()
        jevRequest.incrementAndGet()
        operationRequest.incrementAndGet()
        inspectionRequest.incrementAndGet()
        uiHandler.removeCallbacksAndMessages(null)
        jevExecutor.shutdownNow()
        qwenEngine?.close()
        if (::frameSource.isInitialized) frameSource.close()
        if (::voice.isInitialized) voice.close()
        super.onDestroy()
    }
}
