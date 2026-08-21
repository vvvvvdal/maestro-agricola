package br.org.agroturtles.maestro.platform

import android.Manifest
import android.content.pm.PackageManager
import android.net.Uri
import androidx.activity.ComponentActivity
import androidx.activity.result.contract.ActivityResultContracts
import androidx.core.content.ContextCompat
import androidx.lifecycle.lifecycleScope
import br.org.agroturtles.maestro.BuildConfig
import com.meta.wearable.dat.camera.Camera
import com.meta.wearable.dat.camera.Stream
import com.meta.wearable.dat.camera.addCamera
import com.meta.wearable.dat.camera.types.PhotoData
import com.meta.wearable.dat.camera.types.StreamConfiguration
import com.meta.wearable.dat.camera.types.StreamState
import com.meta.wearable.dat.camera.types.VideoQuality
import com.meta.wearable.dat.core.Wearables
import com.meta.wearable.dat.core.selectors.AutoDeviceSelector
import com.meta.wearable.dat.core.session.DeviceSession
import com.meta.wearable.dat.core.session.DeviceSessionState
import com.meta.wearable.dat.core.types.Permission
import com.meta.wearable.dat.core.types.PermissionStatus
import com.meta.wearable.dat.core.types.RegistrationState
import com.meta.wearable.dat.mockdevice.MockDeviceKit
import com.meta.wearable.dat.mockdevice.api.GlassesModel
import com.meta.wearable.dat.mockdevice.api.MockDeviceKitConfig
import com.meta.wearable.dat.mockdevice.api.MockDeviceKitInterface
import com.meta.wearable.dat.mockdevice.api.MockGlasses
import com.meta.wearable.dat.mockdevice.api.camera.CameraFacing
import java.util.concurrent.atomic.AtomicBoolean
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import kotlinx.coroutines.withTimeout


/**
 * Fronteira DAT 0.9.0. Tipos da Meta não escapam deste source set.
 *
 * Uma captura abre sessão e câmera, recebe uma foto, processa a mídia apenas
 * em memória e encerra os recursos. O MockDeviceKit só é ligado quando o build
 * foi criado explicitamente com `-PmaestroDatMockDevice=true`.
 */
class PlatformFrameSource(
    private val activity: ComponentActivity,
    targetMapJson: String,
    private val detector: QrTargetDetector<PhotoData> = QrTargetDetector(
        ZxingPhotoQrDecoder(),
        QrPayloadPolicy.fromTargetMapJson(targetMapJson),
    ),
) : FrameSource {
    private val scope = activity.lifecycleScope
    private val captureInProgress = AtomicBoolean(false)
    private val mockScenario = DatMockScenario.fromBuildConfig(BuildConfig.DAT_MOCK_SCENARIO)
    private val androidPermissions = buildList {
        add(Manifest.permission.BLUETOOTH_CONNECT)
        if (BuildConfig.DAT_MOCK_DEVICE) add(Manifest.permission.CAMERA)
    }.toTypedArray()

    private var completion: ((Result<TargetObservation>) -> Unit)? = null
    private var initialized = false
    private var session: DeviceSession? = null
    private var camera: Camera? = null
    private var stream: Stream? = null
    private var sessionStateJob: Job? = null
    private var sessionErrorJob: Job? = null
    private var streamStateJob: Job? = null
    private var streamErrorJob: Job? = null
    private var timeoutJob: Job? = null
    private var streamBecameActive = false
    private var photoRequested = false

    private var mockDeviceKit: MockDeviceKitInterface? = null
    private var mockGlasses: MockGlasses? = null
    private var mockTargetUri: Uri? = null

    private val androidPermissionLauncher = activity.registerForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()
    ) { grants ->
        if (!captureInProgress.get()) return@registerForActivityResult
        if (grants.values.all { it }) {
            continueCaptureAfterAndroidPermissions()
        } else {
            finish(Result.failure(DatCaptureException(
                "Permissão necessária para conectar aos óculos"
            )))
        }
    }

    private val wearablePermissionLauncher = activity.registerForActivityResult(
        Wearables.RequestPermissionContract()
    ) { result ->
        if (!captureInProgress.get()) return@registerForActivityResult
        val status = result.getOrDefault(PermissionStatus.Denied)
        if (status == PermissionStatus.Granted) {
            attachCamera()
        } else {
            finish(Result.failure(DatCaptureException(
                "Permissão da câmera dos óculos recusada"
            )))
        }
    }

    override fun captureTarget(completion: (Result<TargetObservation>) -> Unit) {
        if (!captureInProgress.compareAndSet(false, true)) {
            completion(Result.failure(DatCaptureException("Já existe uma captura em andamento")))
            return
        }
        this.completion = completion
        timeoutJob = scope.launch {
            delay(CAPTURE_TIMEOUT_MS)
            finish(Result.failure(DatCaptureException("Tempo esgotado ao capturar o alvo")))
        }

        val missing = androidPermissions.filter {
            ContextCompat.checkSelfPermission(activity, it) != PackageManager.PERMISSION_GRANTED
        }
        if (missing.isEmpty()) {
            continueCaptureAfterAndroidPermissions()
        } else {
            androidPermissionLauncher.launch(missing.toTypedArray())
        }
    }

    private fun continueCaptureAfterAndroidPermissions() {
        if (!captureInProgress.get()) return
        if (!initialized) {
            Wearables.initialize(activity)
                .onSuccess { initialized = true }
                .onFailure { error, _ ->
                    finish(Result.failure(DatCaptureException(
                        "Falha ao inicializar DAT: ${error.description}"
                    )))
                }
            if (!initialized) return
        }

        if (BuildConfig.DAT_MOCK_DEVICE) {
            runCatching(::prepareMockDevice)
                .onFailure { error ->
                    finish(Result.failure(DatCaptureException(
                        error.message ?: "Falha ao preparar MockDeviceKit"
                    )))
                }
                .onSuccess { waitForDeviceAndStartSession() }
            return
        }

        if (Wearables.registrationState.value != RegistrationState.REGISTERED) {
            Wearables.startRegistration(activity)
            finish(Result.failure(DatCaptureException(
                "Conclua o registro no Meta AI e tente capturar novamente"
            )))
            return
        }

        waitForDeviceAndStartSession()
    }

    private fun prepareMockDevice() {
        if (mockGlasses != null) return
        val kit = MockDeviceKit.getInstance(activity.applicationContext)
        val permissionDenied = mockScenario == DatMockScenario.PERMISSION_DENIED
        kit.enable(MockDeviceKitConfig(initialPermissionsGranted = !permissionDenied))
        kit.permissions.set(
            Permission.CAMERA,
            if (permissionDenied) PermissionStatus.Denied else PermissionStatus.Granted,
        )
        if (permissionDenied) {
            kit.permissions.setRequestResult(Permission.CAMERA, PermissionStatus.Denied)
        }
        mockDeviceKit = kit
        if (mockScenario == DatMockScenario.TIMEOUT) return

        val glasses = kit.pairGlasses(GlassesModel.RAYBAN_META).getOrThrow()
        glasses.powerOn()
        glasses.don()
        glasses.unfold()
        glasses.services.camera.setCameraFeed(CameraFacing.BACK)
        val targetUri = Uri.parse(
            "content://${activity.packageName}.datmock/${DatMockAssetProvider.TARGET_ASSET}"
        )
        glasses.services.camera.setCapturedImage(targetUri)
        mockTargetUri = targetUri
        mockGlasses = glasses
    }

    private fun waitForDeviceAndStartSession() {
        if (!captureInProgress.get()) return
        scope.launch {
            runCatching {
                val selector = AutoDeviceSelector()
                withTimeout(DEVICE_TIMEOUT_MS) {
                    selector.activeDeviceFlow().first { it != null }
                }
                selector
            }.onSuccess(::startSession)
                .onFailure {
                    finish(Result.failure(DatCaptureException("Nenhum dispositivo DAT disponível")))
                }
        }
    }

    private fun startSession(selector: AutoDeviceSelector) {
        if (!captureInProgress.get()) return
        Wearables.createSession(selector)
            .onSuccess { created ->
                session = created
                observeSession(created)
                created.start()
            }
            .onFailure { error, _ ->
                finish(Result.failure(DatCaptureException(
                    "Falha ao iniciar sessão DAT: ${error.description}"
                )))
            }
    }

    private fun observeSession(current: DeviceSession) {
        sessionStateJob = scope.launch {
            current.state.collect { state ->
                when (state) {
                    DeviceSessionState.STARTED -> checkCameraPermission()
                    DeviceSessionState.STOPPED -> if (captureInProgress.get()) {
                        finish(Result.failure(DatCaptureException("Sessão DAT encerrada")))
                    }
                    else -> Unit
                }
            }
        }
        sessionErrorJob = scope.launch {
            current.errors.collect { error ->
                finish(Result.failure(DatCaptureException(
                    "Erro na sessão DAT: ${error.description}"
                )))
            }
        }
    }

    private fun checkCameraPermission() {
        if (!captureInProgress.get()) return
        scope.launch {
            Wearables.checkPermissionStatus(Permission.CAMERA)
                .onSuccess { status ->
                    if (status == PermissionStatus.Granted) {
                        attachCamera()
                    } else {
                        wearablePermissionLauncher.launch(Permission.CAMERA)
                    }
                }
                .onFailure { error, _ ->
                    finish(Result.failure(DatCaptureException(
                        "Falha ao consultar permissão da câmera: ${error.description}"
                    )))
                }
        }
    }

    private fun attachCamera() {
        if (!captureInProgress.get()) return
        val current = session ?: run {
            finish(Result.failure(DatCaptureException("Sessão DAT indisponível")))
            return
        }
        if (camera != null) return
        current.addCamera(
            StreamConfiguration(
                videoQuality = VideoQuality.LOW,
                frameRate = FRAME_RATE,
                compressVideo = true,
            )
        ).onSuccess { attached ->
            camera = attached
            stream = attached.stream
            observeStream(attached.stream)
            attached.stream.start().onFailure { error, _ ->
                finish(Result.failure(DatCaptureException(
                    "Falha ao iniciar câmera DAT: ${error.description}"
                )))
            }
        }.onFailure { error, _ ->
            finish(Result.failure(DatCaptureException(
                "Falha ao adicionar câmera DAT: ${error.description}"
            )))
        }
    }

    private fun observeStream(current: Stream) {
        streamStateJob = scope.launch {
            current.state.collect { state ->
                val terminal = state == StreamState.STOPPED || state == StreamState.CLOSED
                if (!terminal) streamBecameActive = true
                if (state == StreamState.STREAMING && !photoRequested) {
                    if (mockScenario == DatMockScenario.DISCONNECT) {
                        photoRequested = true
                        mockGlasses?.powerOff()
                    } else {
                        // No DAT 0.9.0 o feed da câmera física tem prioridade na captura.
                        // Trocar a origem depois que o stream abriu preserva o teste da sessão,
                        // mas faz capturePhoto() consumir a fixture configurada em memória.
                        mockTargetUri?.let { mockGlasses?.services?.camera?.setCameraFeed(it) }
                        capturePhoto(current)
                    }
                }
                if (terminal && streamBecameActive && captureInProgress.get()) {
                    finish(Result.failure(DatCaptureException("Câmera DAT desconectada")))
                }
            }
        }
        streamErrorJob = scope.launch {
            current.errorStream.collect { error ->
                finish(Result.failure(DatCaptureException(
                    "Erro na câmera DAT: ${error.description}"
                )))
            }
        }
    }

    private fun capturePhoto(current: Stream) {
        photoRequested = true
        scope.launch {
            current.capturePhoto()
                .onSuccess { photo ->
                    val observation = withContext(Dispatchers.Default) {
                        detector.detect(photo)
                    }
                    finish(observation)
                }
                .onFailure { error, _ ->
                    finish(Result.failure(DatCaptureException(
                        "Falha ao capturar foto: ${error.description}"
                    )))
                }
        }
    }

    private fun finish(result: Result<TargetObservation>) {
        val callback = completion ?: return
        completion = null
        captureInProgress.set(false)
        timeoutJob?.cancel()
        timeoutJob = null
        cleanupSession()
        callback(result)
    }

    private fun cleanupSession() {
        sessionStateJob?.cancel()
        sessionErrorJob?.cancel()
        streamStateJob?.cancel()
        streamErrorJob?.cancel()
        sessionStateJob = null
        sessionErrorJob = null
        streamStateJob = null
        streamErrorJob = null
        streamBecameActive = false
        photoRequested = false
        camera?.close()
        camera = null
        stream = null
        session?.stop()
        session = null
    }

    override fun cancelCapture() {
        completion = null
        captureInProgress.set(false)
        timeoutJob?.cancel()
        timeoutJob = null
        cleanupSession()
    }

    override fun close() {
        completion = null
        captureInProgress.set(false)
        timeoutJob?.cancel()
        timeoutJob = null
        cleanupSession()
        mockGlasses?.let { mockDeviceKit?.unpairDevice(it) }
        mockGlasses = null
        mockTargetUri = null
        mockDeviceKit?.disable()
        mockDeviceKit = null
    }

    companion object {
        private const val FRAME_RATE = 2
        private const val DEVICE_TIMEOUT_MS = 5_000L
        private const val CAPTURE_TIMEOUT_MS = 20_000L
    }
}


private enum class DatMockScenario {
    SUCCESS,
    PERMISSION_DENIED,
    TIMEOUT,
    DISCONNECT;

    companion object {
        fun fromBuildConfig(value: String): DatMockScenario = when (value) {
            "permission-denied" -> PERMISSION_DENIED
            "timeout" -> TIMEOUT
            "disconnect" -> DISCONNECT
            else -> SUCCESS
        }
    }
}


class DatCaptureException(message: String) : IllegalStateException(message)
