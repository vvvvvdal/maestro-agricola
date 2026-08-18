import Foundation

enum TargetResolutionStatus: String, Equatable {
    case resolved = "RESOLVED"
    case needsVisual = "NEEDS_VISUAL"
    case conflict = "CONFLICT"
    case unknown = "UNKNOWN"
}

struct TargetResolution: Equatable {
    let status: TargetResolutionStatus
    let targetId: String?
    let source: String?
}

struct TargetResolver {
    private struct Catalog: Decodable {
        let targets: [String: [String: Double]]
    }

    private let allowedTargetIds: Set<String>
    private static let numberWords = [
        "zero": 0, "um": 1, "uma": 1, "dois": 2, "duas": 2,
        "tres": 3, "quatro": 4, "cinco": 5, "seis": 6,
        "sete": 7, "oito": 8, "nove": 9,
    ]

    init(allowedTargetIds: Set<String>) {
        self.allowedTargetIds = allowedTargetIds
    }

    init(data: Data) throws {
        let catalog = try JSONDecoder().decode(Catalog.self, from: data)
        allowedTargetIds = Set(catalog.targets.keys)
    }

    func resolve(visualTargetId: String?, transcript: String) -> TargetResolution {
        let visual = Self.canonicalTargetId(visualTargetId)
        let spoken = Self.extractSpokenTargetId(transcript)
        if let visual, let spoken, visual != spoken {
            return TargetResolution(status: .conflict, targetId: nil, source: nil)
        }
        let candidate = visual ?? spoken
        if let candidate, !allowedTargetIds.contains(candidate) {
            return TargetResolution(status: .unknown, targetId: nil, source: nil)
        }
        if visual != nil, spoken != nil {
            return TargetResolution(status: .resolved, targetId: candidate, source: "AGREED")
        }
        if let visual { return TargetResolution(status: .resolved, targetId: visual, source: "VISUAL") }
        if let spoken { return TargetResolution(status: .resolved, targetId: spoken, source: "VOICE") }
        return TargetResolution(status: .needsVisual, targetId: nil, source: nil)
    }

    private static func tokens(_ text: String) -> [String] {
        text.folding(options: [.caseInsensitive, .diacriticInsensitive], locale: Locale(identifier: "pt_BR"))
            .lowercased()
            .split { !$0.isLetter && !$0.isNumber }
            .map(String.init)
    }

    private static func canonicalTargetId(_ value: String?) -> String? {
        guard let value, !value.trimmingCharacters(in: .whitespaces).isEmpty else { return nil }
        let normalized = value.trimmingCharacters(in: .whitespaces).lowercased()
        let compact = normalized.replacingOccurrences(of: "-", with: "")
            .replacingOccurrences(of: "_", with: "")
            .replacingOccurrences(of: " ", with: "")
        guard compact.hasPrefix("plot"), let number = Int(compact.dropFirst(4)) else { return normalized }
        return String(format: "plot-%02d", number)
    }

    private static func extractSpokenTargetId(_ transcript: String) -> String? {
        let values = tokens(transcript)
        for index in values.indices where ["plot", "talhao"].contains(values[index]) {
            guard index + 1 < values.count else { continue }
            let first = values[index + 1]
            var number = Int(first)
            if number == nil, let firstDigit = numberWords[first] {
                let secondDigit = index + 2 < values.count ? numberWords[values[index + 2]] : nil
                number = secondDigit.map { firstDigit * 10 + $0 } ?? firstDigit
            }
            if let number { return String(format: "plot-%02d", number) }
        }
        return nil
    }
}
