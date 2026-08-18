import Foundation
import XCTest
@testable import MaestroAgricola

private struct ParityFixture: Decodable {
    struct Case: Decodable {
        let id: String
        let text: String
        let expectedLabel: String
        let expectedConfidence: Double

        enum CodingKeys: String, CodingKey {
            case id, text
            case expectedLabel = "expected_label"
            case expectedConfidence = "expected_confidence"
        }
    }

    let confidenceTolerance: Double
    let cases: [Case]

    enum CodingKeys: String, CodingKey {
        case confidenceTolerance = "confidence_tolerance"
        case cases
    }
}

final class LocalIntentClassifierParityTests: XCTestCase {
    func testMatchesSharedParityFixture() throws {
        let bundle = Bundle(for: Self.self)
        let modelURL = try XCTUnwrap(bundle.url(forResource: "intent_model", withExtension: "json"))
        let fixtureURL = try XCTUnwrap(bundle.url(forResource: "parity_cases", withExtension: "json"))
        let classifier = try LocalIntentClassifier(data: Data(contentsOf: modelURL))
        let fixture = try JSONDecoder().decode(
            ParityFixture.self,
            from: Data(contentsOf: fixtureURL)
        )

        for item in fixture.cases {
            let prediction = classifier.classify(item.text)
            XCTAssertEqual(item.expectedLabel, prediction.label, item.id)
            XCTAssertEqual(
                item.expectedConfidence,
                prediction.confidence,
                accuracy: fixture.confidenceTolerance,
                item.id
            )
        }
    }
}
