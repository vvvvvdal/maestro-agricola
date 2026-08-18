import XCTest
@testable import MaestroAgricola

private final class SequenceClassifier: IntentClassifying {
    private var labels: [String]

    init(_ labels: [String]) { self.labels = labels }

    func classify(_ text: String) -> IntentPrediction {
        IntentPrediction(label: labels.removeFirst(), confidence: 0.99)
    }
}

final class InteractionEngineTests: XCTestCase {
    func testRequiresConfirmationBeforeCommand() {
        let engine = InteractionEngine(classifier: SequenceClassifier(["SPRAY", "CONFIRM"]))
        _ = engine.observeTarget("plot-03")
        XCTAssertNil(engine.handleTranscript("pulverizar").command)
        XCTAssertNotNil(engine.handleTranscript("confirmar").command)
    }

    func testCancelAndTimeoutNeverCreateCommand() {
        let engine = InteractionEngine(classifier: SequenceClassifier(["SPRAY", "CANCEL"]))
        _ = engine.observeTarget("plot-03")
        _ = engine.handleTranscript("pulverizar")
        XCTAssertNil(engine.handleTranscript("cancelar").command)

        let timeoutEngine = InteractionEngine(classifier: SequenceClassifier(["SPRAY"]))
        _ = timeoutEngine.observeTarget("plot-03")
        _ = timeoutEngine.handleTranscript("pulverizar")
        XCTAssertNil(timeoutEngine.confirmationTimedOut().command)
    }

    func testExplicitSpokenTargetWorksWithoutVisualMarker() {
        let engine = InteractionEngine(classifier: SequenceClassifier(["SPRAY", "CONFIRM"]))
        XCTAssertNil(engine.handleTranscript("pulverize no plot-03").command)
        XCTAssertEqual("plot-03", engine.handleTranscript("confirmar").command?.target.id)
    }

    func testVisualAndSpokenConflictNeverCreatesCommand() {
        let engine = InteractionEngine(classifier: SequenceClassifier(["SPRAY"]))
        _ = engine.observeTarget("plot-03")
        let conflict = engine.handleTranscript("pulverize no plot quatro")
        XCTAssertEqual(.ambiguous, conflict.state)
        XCTAssertNil(conflict.command)
    }
}
