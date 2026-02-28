import SwiftUI

@main
struct HoopShotApp: App {
    @State private var token: String? = nil

    var body: some Scene {
        WindowGroup {
            if let token {
                GameView(token: token)
            } else {
                LoginView(token: $token)
            }
        }
    }
}
