import Foundation

enum InteractionState: String {
    case idle = "IDLE"
    case targetReady = "TARGET_READY"
    case awaitingConfirmation = "AWAITING_CONFIRMATION"
    case sending = "SENDING"
    case accepted = "ACCEPTED"
    case cancelled = "CANCELLED"
    case ambiguous = "AMBIGUOUS"
    case error = "ERROR"
}

struct RobotCommand: Encodable, Equatable {
    struct Target: Encodable, Equatable {
        let type: String
        let id: String
    }

    let schemaVersion = "1.0"
    let commandId: String
    let createdAt: String
    let expiresInMs = 5_000
    let intent = "SPRAY"
    let target: Target
    let confirmed = true

    enum CodingKeys: String, CodingKey {
        case schemaVersion = "schema_version"
        case commandId = "command_id"
        case createdAt = "created_at"
        case expiresInMs = "expires_in_ms"
        case intent, target, confirmed
    }
}

struct InteractionResult {
    let state: InteractionState
    let message: String
    let speech: String?
    let command: RobotCommand?
    let prediction: IntentPrediction?
}

final class InteractionEngine {
    private let classifier: IntentClassifying
    private let targetResolver: TargetResolver
    private var visualTargetId: String?
    private var targetId: String?
    private(set) var state: InteractionState = .idle

    init(
        classifier: IntentClassifying,
        targetResolver: TargetResolver = TargetResolver(
            allowedTargetIds: ["plot-01", "plot-02", "plot-03"]
        )
    ) {
        self.classifier = classifier
        self.targetResolver = targetResolver
    }

    func observeTarget(_ id: String) -> InteractionResult {
        visualTargetId = id
        targetId = nil
        state = .targetReady
        return result("Alvo \(id) identificado", speech: "Alvo \(id) identificado")
    }

    func handleTranscript(_ text: String) -> InteractionResult {
        let prediction = classifier.classify(text)
        switch state {
        case .idle, .targetReady:
            guard prediction.label == "SPRAY" else {
                return ambiguous("Intenção não reconhecida", prediction)
            }
            let resolution = targetResolver.resolve(visualTargetId: visualTargetId, transcript: text)
            guard resolution.status == .resolved, let resolvedTargetId = resolution.targetId else {
                targetId = nil
                state = .ambiguous
                let message: String
                switch resolution.status {
                case .conflict: message = "Alvo falado e visual não conferem"
                case .unknown: message = "Alvo não cadastrado"
                case .needsVisual: message = "Olhe para a placa ou diga o ID do plot"
                case .resolved: preconditionFailure("estado impossível")
                }
                return result(message, speech: "\(message). Operação cancelada", prediction: prediction)
            }
            targetId = resolvedTargetId
            state = .awaitingConfirmation
            return result(
                "Pulverizar \(resolvedTargetId)?",
                speech: "Pulverizar \(resolvedTargetId.replacingOccurrences(of: "plot-", with: "talhão ")), confirmar?",
                prediction: prediction
            )
        case .awaitingConfirmation:
            if prediction.label == "CONFIRM", let targetId {
                state = .sending
                let command = RobotCommand(
                    commandId: UUID().uuidString.lowercased(),
                    createdAt: ISO8601DateFormatter().string(from: Date()),
                    target: .init(type: "MAPPED_PLOT", id: targetId)
                )
                return result("Enviando comando", command: command, prediction: prediction)
            }
            if prediction.label == "CANCEL" {
                state = .cancelled
                return result("Operação cancelada", speech: "Operação cancelada", prediction: prediction)
            }
            return ambiguous("Confirmação ambígua", prediction)
        default:
            return ambiguous("Inicie uma nova interação", prediction)
        }
    }

    func confirmationTimedOut() -> InteractionResult {
        guard state == .awaitingConfirmation else { return result("Nenhuma confirmação pendente") }
        targetId = nil
        visualTargetId = nil
        state = .cancelled
        return result("Confirmação expirada", speech: "Tempo esgotado. Operação cancelada")
    }

    func transportCompleted(accepted: Bool, reason: String) -> InteractionResult {
        state = accepted ? .accepted : .error
        return result(reason, speech: accepted ? "Comando enviado" : "Comando recusado")
    }

    func reset() -> InteractionResult {
        targetId = nil
        visualTargetId = nil
        state = .idle
        return result("Pronto para iniciar")
    }

    private func ambiguous(_ message: String, _ prediction: IntentPrediction) -> InteractionResult {
        return result(message, speech: "Não entendi. Tente novamente", prediction: prediction)
    }

    private func result(
        _ message: String,
        speech: String? = nil,
        command: RobotCommand? = nil,
        prediction: IntentPrediction? = nil
    ) -> InteractionResult {
        InteractionResult(
            state: state,
            message: message,
            speech: speech,
            command: command,
            prediction: prediction
        )
    }
}
