import Foundation

struct CommandResponse: Decodable {
    let schemaVersion: String
    let commandId: String
    let status: String
    let reason: String?

    enum CodingKeys: String, CodingKey {
        case schemaVersion = "schema_version"
        case commandId = "command_id"
        case status, reason
    }
}

protocol CommandTransporting {
    func send(_ command: RobotCommand, to endpoint: URL) async throws -> CommandResponse
}

struct WebSocketCommandTransport: CommandTransporting {
    func send(_ command: RobotCommand, to endpoint: URL) async throws -> CommandResponse {
        let socket = URLSession.shared.webSocketTask(with: endpoint)
        socket.resume()
        defer { socket.cancel(with: .normalClosure, reason: nil) }
        let data = try JSONEncoder().encode(command)
        try await socket.send(.data(data))
        let message = try await socket.receive()
        let responseData: Data
        switch message {
        case .data(let data): responseData = data
        case .string(let text): responseData = Data(text.utf8)
        @unknown default: throw TransportError.invalidResponse
        }
        let response = try JSONDecoder().decode(CommandResponse.self, from: responseData)
        guard response.schemaVersion == "1.0" else { throw TransportError.invalidResponse }
        guard response.commandId == command.commandId else { throw TransportError.commandMismatch }
        return response
    }
}

enum TransportError: Error {
    case invalidResponse
    case commandMismatch
}
