import AVFoundation
import Foundation
import Speech

@MainActor
final class VoiceIO {
    private let recognizer = SFSpeechRecognizer(locale: Locale(identifier: "pt_BR"))
    private let audioEngine = AVAudioEngine()
    private let synthesizer = AVSpeechSynthesizer()
    private var recognitionTask: SFSpeechRecognitionTask?
    private var pendingContinuation: CheckedContinuation<String, any Error>?

    func listen() async throws -> String {
        let authorized = await withCheckedContinuation { continuation in
            SFSpeechRecognizer.requestAuthorization { status in
                continuation.resume(returning: status == .authorized)
            }
        }
        guard authorized else { throw VoiceError.notAuthorized }
        let microphoneAuthorized = await withCheckedContinuation { continuation in
            AVAudioApplication.requestRecordPermission { granted in
                continuation.resume(returning: granted)
            }
        }
        guard microphoneAuthorized else { throw VoiceError.microphoneNotAuthorized }
        guard let recognizer, recognizer.isAvailable, recognizer.supportsOnDeviceRecognition else {
            throw VoiceError.onDeviceRecognitionUnavailable
        }

        let session = AVAudioSession.sharedInstance()
        try session.setCategory(.playAndRecord, mode: .spokenAudio, options: [.allowBluetooth, .defaultToSpeaker])
        try session.setActive(true, options: .notifyOthersOnDeactivation)

        let request = SFSpeechAudioBufferRecognitionRequest()
        request.requiresOnDeviceRecognition = true
        request.shouldReportPartialResults = false
        let input = audioEngine.inputNode
        let format = input.outputFormat(forBus: 0)
        input.installTap(onBus: 0, bufferSize: 1_024, format: format) { buffer, _ in
            request.append(buffer)
        }

        do {
            audioEngine.prepare()
            try audioEngine.start()
            return try await withCheckedThrowingContinuation { continuation in
                pendingContinuation = continuation
                recognitionTask = recognizer.recognitionTask(with: request) { [weak self] result, error in
                    let text = result?.bestTranscription.formattedString
                    let isFinal = result?.isFinal == true
                    let errorMessage = error?.localizedDescription
                    Task { @MainActor [weak self] in
                        self?.completeRecognition(
                            text: text,
                            isFinal: isFinal,
                            errorMessage: errorMessage
                        )
                    }
                }
            }
        } catch {
            stopListening()
            throw error
        }
    }

    func speak(_ text: String) {
        let utterance = AVSpeechUtterance(string: text)
        utterance.voice = AVSpeechSynthesisVoice(language: "pt-BR")
        synthesizer.speak(utterance)
    }

    private func stopListening() {
        recognitionTask?.cancel()
        recognitionTask = nil
        if audioEngine.isRunning { audioEngine.stop() }
        audioEngine.inputNode.removeTap(onBus: 0)
    }

    private func completeRecognition(text: String?, isFinal: Bool, errorMessage: String?) {
        guard let continuation = pendingContinuation else { return }
        if let text, isFinal {
            pendingContinuation = nil
            stopListening()
            continuation.resume(returning: text)
        } else if let errorMessage {
            pendingContinuation = nil
            stopListening()
            continuation.resume(throwing: VoiceError.recognitionFailed(errorMessage))
        }
    }
}

enum VoiceError: Error {
    case notAuthorized
    case microphoneNotAuthorized
    case onDeviceRecognitionUnavailable
    case recognitionFailed(String)
}
