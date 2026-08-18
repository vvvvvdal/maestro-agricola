import Foundation
import Observation

@Observable
@MainActor
final class MaestroViewModel {
    var interaction: InteractionResult
    var transcript = ""
    var endpoint = "ws://127.0.0.1:18765"

    private let engine: InteractionEngine
    private let frameSource: FrameSource
    private let transport: CommandTransporting
    private let voice: VoiceIO

    init(
        engine: InteractionEngine,
        frameSource: FrameSource,
        transport: CommandTransporting,
        voice: VoiceIO
    ) {
        self.engine = engine
        self.frameSource = frameSource
        self.transport = transport
        self.voice = voice
        interaction = engine.reset()
    }

    static func bootstrap() -> MaestroViewModel {
        do {
            guard let url = Bundle.main.url(forResource: "intent_model", withExtension: "json") else {
                throw ClassifierError.missingModel
            }
            guard let targetMapURL = Bundle.main.url(forResource: "targets", withExtension: "json") else {
                throw ClassifierError.missingTargetMap
            }
            let classifier = try LocalIntentClassifier(data: Data(contentsOf: url))
            return MaestroViewModel(
                engine: InteractionEngine(
                    classifier: classifier,
                    targetResolver: try TargetResolver(data: Data(contentsOf: targetMapURL))
                ),
                frameSource: MockFrameSource(),
                transport: WebSocketCommandTransport(),
                voice: VoiceIO()
            )
        } catch {
            fatalError("Modelo local inválido: \(error)")
        }
    }

    func observeTarget() async {
        do {
            apply(engine.observeTarget(try await frameSource.captureTarget()))
        } catch {
            apply(engine.reset(), overridingMessage: error.localizedDescription)
        }
    }

    func interpret() { apply(engine.handleTranscript(transcript)) }

    func listen() async {
        do {
            transcript = try await voice.listen()
            interpret()
        } catch {
            apply(engine.reset(), overridingMessage: error.localizedDescription)
        }
    }

    func timeOutConfirmation() { apply(engine.confirmationTimedOut()) }
    func reset() { apply(engine.reset()) }

    private func apply(_ result: InteractionResult, overridingMessage: String? = nil) {
        interaction = overridingMessage.map {
            InteractionResult(
                state: result.state,
                message: $0,
                speech: result.speech,
                command: result.command,
                prediction: result.prediction
            )
        } ?? result
        if let speech = result.speech { voice.speak(speech) }
        if let command = result.command { Task { await send(command) } }
    }

    private func send(_ command: RobotCommand) async {
        guard let url = URL(string: endpoint) else {
            apply(engine.transportCompleted(accepted: false, reason: "URL do bridge inválida"))
            return
        }
        do {
            let response = try await transport.send(command, to: url)
            apply(engine.transportCompleted(
                accepted: response.status == "ACCEPTED",
                reason: response.reason ?? response.status
            ))
        } catch {
            apply(engine.transportCompleted(accepted: false, reason: error.localizedDescription))
        }
    }
}
