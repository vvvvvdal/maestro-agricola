import SwiftUI

struct ContentView: View {
    @Bindable var viewModel: MaestroViewModel

    var body: some View {
        NavigationStack {
            Form {
                Section("Execução") {
                    LabeledContent("Fonte", value: "mock")
                    LabeledContent("Estado", value: viewModel.interaction.state.rawValue)
                    Text(viewModel.interaction.message)
                    if let prediction = viewModel.interaction.prediction {
                        LabeledContent(
                            "IA",
                            value: "\(prediction.label) · \(prediction.confidence.formatted(.percent.precision(.fractionLength(1))))"
                        )
                    }
                }
                Section("Comando") {
                    TextField("Transcrição para teste", text: $viewModel.transcript)
                    TextField("Bridge WebSocket", text: $viewModel.endpoint)
                        .textInputAutocapitalization(.never)
                        .autocorrectionDisabled()
                    Text("No iPhone físico, use o IP do computador.")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                    Button("Simular olhar") { Task { await viewModel.observeTarget() } }
                    Button("Interpretar") { viewModel.interpret() }
                    Button("Falar") { Task { await viewModel.listen() } }
                    Button("Reiniciar", role: .cancel) { viewModel.reset() }
                }
            }
            .navigationTitle("Maestro Agrícola")
            .task(id: viewModel.interaction.state) {
                guard viewModel.interaction.state == .awaitingConfirmation else { return }
                try? await Task.sleep(for: .seconds(10))
                guard !Task.isCancelled else { return }
                viewModel.timeOutConfirmation()
            }
        }
    }
}
