import Foundation

struct IntentPrediction: Equatable {
    let label: String
    let confidence: Double
}

protocol IntentClassifying {
    func classify(_ text: String) -> IntentPrediction
}

struct LocalIntentClassifier: IntentClassifying {
    private struct Payload: Decodable {
        let model_type: String
        let labels: [String]
        let bias: [String: Double]
        let weights: [String: [String: Double]]
    }

    private let payload: Payload
    private let vocabulary: Set<String>
    private let threshold: Double

    init(data: Data, threshold: Double = 0.40) throws {
        let decoded = try JSONDecoder().decode(Payload.self, from: data)
        guard decoded.model_type == "linear_softmax" else {
            throw ClassifierError.unsupportedModel
        }
        payload = decoded
        vocabulary = Set(decoded.weights.values.flatMap(\.keys))
        self.threshold = threshold
    }

    func classify(_ text: String) -> IntentPrediction {
        let current = features(text).intersection(vocabulary)
        guard !current.isEmpty else { return IntentPrediction(label: "UNKNOWN", confidence: 1) }

        let scores = Dictionary(uniqueKeysWithValues: payload.labels.map { label in
            let score = payload.bias[label, default: 0] + current.reduce(0) {
                $0 + (payload.weights[label]?[$1] ?? 0)
            }
            return (label, score)
        })
        guard let best = scores.max(by: { $0.value < $1.value }) else {
            return IntentPrediction(label: "UNKNOWN", confidence: 1)
        }
        let peak = best.value
        let denominator = scores.values.reduce(0) { $0 + exp($1 - peak) }
        let confidence = exp(best.value - peak) / denominator
        if best.key != "UNKNOWN" && confidence < threshold {
            return IntentPrediction(label: "UNKNOWN", confidence: confidence)
        }
        return IntentPrediction(label: best.key, confidence: confidence)
    }

    private func features(_ text: String) -> Set<String> {
        let normalized = text.folding(
            options: [.caseInsensitive, .diacriticInsensitive],
            locale: Locale(identifier: "pt_BR")
        ).lowercased()
        let tokens = normalized.split { !$0.isLetter && !$0.isNumber }.map(String.init)
        var values = Set(tokens.map { "u:\($0)" })
        for token in tokens where token.count >= 6 {
            values.insert("p6:\(token.prefix(6))")
            values.insert("s6:\(token.suffix(6))")
        }
        for pair in zip(tokens, tokens.dropFirst()) {
            values.insert("b:\(pair.0)_\(pair.1)")
        }
        return values
    }
}

enum ClassifierError: Error {
    case unsupportedModel
    case missingModel
}
