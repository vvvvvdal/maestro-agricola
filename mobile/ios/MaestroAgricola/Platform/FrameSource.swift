import Foundation

protocol FrameSource {
    func captureTarget() async throws -> String
}

struct MockFrameSource: FrameSource {
    func captureTarget() async throws -> String { "plot-03" }
}

