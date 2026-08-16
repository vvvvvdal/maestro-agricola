import Foundation
import MWDATCamera
import MWDATCore

struct DatFrameSource: FrameSource {
    func captureTarget() async throws -> String {
        throw DatFrameSourceError.notConnected
    }
}

enum DatFrameSourceError: LocalizedError {
    case notConnected

    var errorDescription: String? {
        "Conecte aqui o ciclo oficial Wearables -> DeviceSession -> Camera -> Stream.capturePhoto()."
    }
}

