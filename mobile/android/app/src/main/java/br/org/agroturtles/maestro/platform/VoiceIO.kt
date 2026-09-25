package br.org.agroturtles.maestro.platform

import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.speech.RecognitionListener
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import android.speech.tts.TextToSpeech
import android.speech.tts.UtteranceProgressListener
import java.util.Locale
import java.util.concurrent.atomic.AtomicLong


class VoiceIO(context: Context) : RecognitionListener, TextToSpeech.OnInitListener {
    private val recognizer = SpeechRecognizer.createSpeechRecognizer(context)
    private val tts = TextToSpeech(context, this)
    private val mainHandler = Handler(Looper.getMainLooper())
    private val speechRequest = AtomicLong(0)
    private var completion: ((Result<String>) -> Unit)? = null
    private var spokenCompletion: (() -> Unit)? = null
    private var activeUtteranceId: String? = null

    init {
        recognizer.setRecognitionListener(this)
        tts.setOnUtteranceProgressListener(object : UtteranceProgressListener() {
            override fun onStart(utteranceId: String) = Unit

            override fun onDone(utteranceId: String) = finishSpeech(utteranceId)

            @Suppress("OVERRIDE_DEPRECATION")
            @Deprecated("Deprecated in Java")
            override fun onError(utteranceId: String) = finishSpeech(utteranceId)

            override fun onError(utteranceId: String, errorCode: Int) = finishSpeech(utteranceId)

            private fun finishSpeech(utteranceId: String) {
                if (utteranceId != activeUtteranceId) return
                val callback = spokenCompletion ?: return
                activeUtteranceId = null
                spokenCompletion = null
                mainHandler.post(callback)
            }
        })
    }

    fun listen(completion: (Result<String>) -> Unit) {
        this.completion = completion
        val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH)
            .putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            .putExtra(RecognizerIntent.EXTRA_LANGUAGE, "pt-BR")
            .putExtra(RecognizerIntent.EXTRA_PREFER_OFFLINE, true)
            .putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 1)
        recognizer.startListening(intent)
    }

    fun speak(text: String, onFinished: (() -> Unit)? = null) {
        val utteranceId = "maestro-${speechRequest.incrementAndGet()}"
        activeUtteranceId = utteranceId
        spokenCompletion = onFinished
        tts.speak(text, TextToSpeech.QUEUE_FLUSH, null, utteranceId)
    }

    fun close() {
        recognizer.destroy()
        tts.shutdown()
    }

    override fun onInit(status: Int) {
        if (status == TextToSpeech.SUCCESS) tts.language = Locale.forLanguageTag("pt-BR")
    }

    override fun onResults(results: Bundle) {
        val text = results.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)?.firstOrNull()
        completion?.invoke(text?.let { Result.success(it) } ?: Result.failure(Exception("Sem fala")))
        completion = null
    }

    override fun onError(error: Int) {
        completion?.invoke(Result.failure(Exception("Falha de reconhecimento: $error")))
        completion = null
    }

    override fun onReadyForSpeech(params: Bundle?) = Unit
    override fun onBeginningOfSpeech() = Unit
    override fun onRmsChanged(rmsdB: Float) = Unit
    override fun onBufferReceived(buffer: ByteArray?) = Unit
    override fun onEndOfSpeech() = Unit
    override fun onPartialResults(partialResults: Bundle?) = Unit
    override fun onEvent(eventType: Int, params: Bundle?) = Unit
}
