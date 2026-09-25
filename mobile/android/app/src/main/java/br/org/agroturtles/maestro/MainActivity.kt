package br.org.agroturtles.maestro

import android.Manifest
import android.os.Bundle
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
import br.org.agroturtles.maestro.domain.JevIntentClassifier
import br.org.agroturtles.maestro.domain.LanguageDispatch
import br.org.agroturtles.maestro.domain.LanguageInteractionController
import br.org.agroturtles.maestro.domain.LocalIntentClassifier
import br.org.agroturtles.maestro.domain.QwenDomainAssistant
import br.org.agroturtles.maestro.domain.RemoteTranscriptBlockReason
import br.org.agroturtles.maestro.domain.RemoteTranscriptDecision
import br.org.agroturtles.maestro.domain.RemoteTranscriptGate
import br.org.agroturtles.maestro.domain.TargetResolver
import br.org.agroturtles.maestro.platform.NativeQwenEngine
import br.org.agroturtles.maestro.platform.PlatformFrameSource
import br.org.agroturtles.maestro.platform.VoiceIO
import br.org.agroturtles.maestro.platform.WebSocketCommandTransport
import br.org.agroturtles.maestro.platform.JevProxyChoiceEvaluator
import br.org.agroturtles.maestro.ui.MaestroScreen
import br.org.agroturtles.maestro.ui.MaestroTheme
import br.org.agroturtles.maestro.ui.UnknownRobotPresentation
import br.org.agroturtles.maestro.ui.robotPresentation
import java.io.File
import java.util.concurrent.Executors
import java.util.concurrent.atomic.AtomicLong


private const val DEFAULT_ENDPOINT = "ws://10.0.2.2:18765"
private const val QWEN_MODEL_FILENAME = "qwen2.5-1.5b-q4_k_m.gguf"
private const val ASSISTANT_PROCESSING_MESSAGE = "Processando resposta local…"
private const val ASSISTANT_ERROR_MESSAGE =
    "Assistente local indisponível. Nada foi enviado ao robô."


class MainActivity : ComponentActivity() {
    private lateinit var voice: VoiceIO
    private lateinit var frameSource: PlatformFrameSource
    private var qwenEngine: NativeQwenEngine? = null
    private var languageController: LanguageInteractionController? = null
    private val jevExecutor = Executors.newSingleThreadExecutor()
    private val jevRequest = AtomicLong(0)
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
        val engine = InteractionEngine(
            classifier,
            TargetResolver.fromJson(targetMapJson),
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
        setContent {
            var result by remember { mutableStateOf(engine.reset()) }
            var transcript by remember { mutableStateOf("") }
            var endpoint by remember { mutableStateOf(DEFAULT_ENDPOINT) }
            var robot by remember { mutableStateOf(UnknownRobotPresentation) }
            var secondsToExpire by remember { mutableIntStateOf(0) }
            var jevRemoteEnabled by remember { mutableStateOf(false) }
            var jevRemoteConsent by remember { mutableStateOf(false) }
            var jevPending by remember { mutableStateOf(false) }
            var remoteSessionConsentPrompt by remember { mutableStateOf(false) }
            var remoteBlockReason by remember { mutableStateOf<RemoteTranscriptBlockReason?>(null) }

            fun apply(next: InteractionResult) {
                result = next
                if (next.state == InteractionState.ACCEPTED && next.command != null) {
                    robot = robotPresentation(next.intent, next.targetId)
                }
                next.speech?.let(voice::speak)
                next.command?.let { command ->
                    WebSocketCommandTransport(endpoint).send(command) { accepted, reason ->
                        runOnUiThread { apply(engine.transportCompleted(accepted, reason)) }
                    }
                }
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

            fun interpret(text: String) {
                if (jevPending) return
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
                apply(engine.confirmationTimedOut())
            }

            MaestroTheme {
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
                    onEndpointChange = { endpoint = it },
                    transcript = transcript,
                    onTranscriptChange = { transcript = it },
                    secondsToExpire = secondsToExpire,
                    interactionPending = jevPending,
                    remoteSessionConsentPrompt = remoteSessionConsentPrompt,
                    remoteBlockReason = remoteBlockReason,
                    onConfirmRemoteSession = {
                        remoteSessionConsentPrompt = false
                        jevRemoteConsent = true
                    },
                    onDismissRemoteSession = { remoteSessionConsentPrompt = false },
                    onDismissRemoteBlock = { remoteBlockReason = null },
                    onLook = {
                        jevRequest.incrementAndGet()
                        jevPending = false
                        language.cancelAssistant()
                        frameSource.captureTarget { outcome ->
                            runOnUiThread {
                                outcome
                                    .onSuccess { apply(engine.observeTarget(it.targetId)) }
                                    .onFailure {
                                        apply(engine.targetCaptureFailed(
                                            it.message ?: "Falha ao capturar o alvo"
                                        ))
                                    }
                            }
                        }
                    },
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
                    onReset = {
                        jevRequest.incrementAndGet()
                        jevPending = false
                        remoteSessionConsentPrompt = false
                        remoteBlockReason = null
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
        jevExecutor.shutdownNow()
        qwenEngine?.close()
        if (::frameSource.isInitialized) frameSource.close()
        if (::voice.isInitialized) voice.close()
        super.onDestroy()
    }
}
