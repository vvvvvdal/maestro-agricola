import MWDATCore
import SwiftUI

@main
struct MaestroAgricolaApp: App {
    init() {
        do {
            try Wearables.configure()
        } catch {
            NSLog("[Maestro] DAT ainda não configurado: \(error.localizedDescription)")
        }
    }

    var body: some Scene {
        WindowGroup {
            ContentView(viewModel: MaestroViewModel.bootstrap())
        }
    }
}

