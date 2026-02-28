import SwiftUI

struct LoginView: View {
    @State private var username = ""
    @State private var password = ""
    @State private var isLoading = false
    @State private var errorMessage = ""
    @Binding var token: String?

    var body: some View {
        ZStack {
            Color(red: 0.07, green: 0.1, blue: 0.18).ignoresSafeArea()

            VStack(spacing: 24) {
                VStack(spacing: 8) {
                    Text("🏀").font(.system(size: 72))
                    Text("HoopShot").font(.largeTitle.bold()).foregroundColor(.white)
                    Text("Basketball score tracker")
                        .font(.subheadline)
                        .foregroundColor(.gray)
                }

                VStack(spacing: 16) {
                    TextField("Username", text: $username)
                        .textInputAutocapitalization(.never)
                        .autocorrectionDisabled()
                        .padding()
                        .background(Color(white: 0.15))
                        .cornerRadius(10)
                        .foregroundColor(.white)

                    SecureField("Password", text: $password)
                        .padding()
                        .background(Color(white: 0.15))
                        .cornerRadius(10)
                        .foregroundColor(.white)

                    if !errorMessage.isEmpty {
                        Text(errorMessage)
                            .foregroundColor(.red)
                            .font(.footnote)
                    }

                    Button(action: handleLogin) {
                        if isLoading {
                            ProgressView().tint(.white)
                        } else {
                            Text("Sign In")
                                .font(.headline)
                                .foregroundColor(.white)
                                .frame(maxWidth: .infinity)
                        }
                    }
                    .padding()
                    .background(Color.orange)
                    .cornerRadius(10)
                    .disabled(isLoading || username.isEmpty || password.isEmpty)
                }
                .padding(.horizontal, 32)
            }
        }
    }

    private func handleLogin() {
        isLoading = true
        errorMessage = ""
        Task {
            do {
                let t = try await APIService.shared.login(username: username, password: password)
                await MainActor.run { token = t }
            } catch {
                await MainActor.run {
                    errorMessage = error.localizedDescription
                    isLoading = false
                }
            }
        }
    }
}
