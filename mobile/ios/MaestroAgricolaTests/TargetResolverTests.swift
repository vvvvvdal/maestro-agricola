import Foundation
import XCTest
@testable import MaestroAgricola

private struct TargetResolutionFixture: Decodable {
    struct Case: Decodable {
        let id: String
        let visualTargetId: String?
        let transcript: String
        let expectedStatus: String
        let expectedTargetId: String?
        let expectedSource: String?

        enum CodingKeys: String, CodingKey {
            case id, transcript
            case visualTargetId = "visual_target_id"
            case expectedStatus = "expected_status"
            case expectedTargetId = "expected_target_id"
            case expectedSource = "expected_source"
        }
    }

    let allowedTargetIds: [String]
    let cases: [Case]

    enum CodingKeys: String, CodingKey {
        case allowedTargetIds = "allowed_target_ids"
        case cases
    }
}

final class TargetResolverTests: XCTestCase {
    func testMatchesSharedTargetResolutionCases() throws {
        let bundle = Bundle(for: TargetResolverTests.self)
        let url = try XCTUnwrap(bundle.url(forResource: "target_resolution_cases", withExtension: "json"))
        let fixture = try JSONDecoder().decode(TargetResolutionFixture.self, from: Data(contentsOf: url))
        let resolver = TargetResolver(allowedTargetIds: Set(fixture.allowedTargetIds))
        for item in fixture.cases {
            let result = resolver.resolve(visualTargetId: item.visualTargetId, transcript: item.transcript)
            XCTAssertEqual(item.expectedStatus, result.status.rawValue, item.id)
            XCTAssertEqual(item.expectedTargetId, result.targetId, item.id)
            XCTAssertEqual(item.expectedSource, result.source, item.id)
        }
    }
}
