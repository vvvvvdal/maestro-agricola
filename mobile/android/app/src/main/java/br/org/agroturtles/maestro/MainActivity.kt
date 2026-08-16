package br.org.agroturtles.maestro

import android.Manifest
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.getValue
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.delay
import br.org.agroturtles.maestro.domain.InteractionEngine
import br.org.agroturtles.maestro.domain.InteractionResult
import br.org.agroturtles.maestro.domain.LocalIntentClassifier
import br.org.agroturtles.maestro.platform.PlatformFrameSource
import br.org.agroturtles.maestro.platform.VoiceIO
import br.org.agroturtles.maestro.platform.WebSocketCommandTransport


class MainActivity : ComponentActivity() {
    private lateinit var voice: VoiceIO
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
        val engine = InteractionEngine(LocalIntentClassifier.fromJson(modelJson))
        val frameSource = PlatformFrameSource()
        setContent {
            var result by remember { mutableStateOf(engine.reset()) }
            var transcript by remember { mutableStateOf("") }
            var endpoint by remember { mutableStateOf("ws://10.0.2.2:8765") }

            fun apply(next: InteractionResult) {
                result = next
                next.speech?.let(voice::speak)
                next.command?.let { command ->
                    WebSocketCommandTransport(endpoint).send(command) { accepted, reason ->
                        runOnUiThread { apply(engine.transportCompleted(accepted, reason)) }
                    }
                }
            }

            LaunchedEffect(result.state) {
                if (result.state == br.org.agroturtles.maestro.domain.InteractionState.AWAITING_CONFIRMATION) {
                    delay(10_000)
                    apply(engine.confirmationTimedOut())
                }
            }

            MaterialTheme {
                Surface(modifier = Modifier.fillMaxSize()) {
                    Column(
                        modifier = Modifier.padding(24.dp),
                        verticalArrangement = Arrangement.spacedBy(16.dp),
                    ) {
                        Text("Maestro Agrícola", style = MaterialTheme.typography.headlineMedium)
                        Text("Fonte: ${BuildConfig.FRAME_SOURCE}")
                        Text("Estado: ${result.state}")
                        Text(result.message)
                        result.prediction?.let {
                            Text("IA: ${it.label} (${String.format("%.1f", it.confidence * 100)}%)")
                        }
                        OutlinedTextField(
                            value = transcript,
                            onValueChange = { transcript = it },
                            label = { Text("Transcrição para teste") },
                            modifier = Modifier.fillMaxWidth(),
                        )
                        OutlinedTextField(
                            value = endpoint,
                            onValueChange = { endpoint = it },
                            label = { Text("Bridge WebSocket") },
                            supportingText = { Text("Em celular físico, use o IP do computador") },
                            modifier = Modifier.fillMaxWidth(),
                        )
                        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                            Button(onClick = {
                                frameSource.captureTarget { outcome ->
                                    runOnUiThread {
                                        outcome
                                            .onSuccess { apply(engine.observeTarget(it)) }
                                            .onFailure {
                                                apply(engine.reset().copy(message = it.message ?: "Falha"))
                                            }
                                    }
                                }
                            }) { Text("Simular olhar") }
                            Button(onClick = { apply(engine.handleTranscript(transcript)) }) {
                                Text("Interpretar")
                            }
                        }
                        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                            Button(onClick = {
                                onMicrophoneGranted = {
                                    voice.listen { outcome ->
                                        runOnUiThread {
                                            outcome.onSuccess {
                                                transcript = it
                                                apply(engine.handleTranscript(it))
                                            }
                                            outcome.onFailure {
                                                apply(engine.reset().copy(message = it.message ?: "Falha de voz"))
                                            }
                                        }
                                    }
                                }
                                microphonePermission.launch(Manifest.permission.RECORD_AUDIO)
                            }) { Text("Falar") }
                            Button(onClick = { apply(engine.reset()) }) { Text("Reiniciar") }
                        }
                    }
                }
            }
        }
    }

    override fun onDestroy() {
        voice.close()
        super.onDestroy()
    }
}
