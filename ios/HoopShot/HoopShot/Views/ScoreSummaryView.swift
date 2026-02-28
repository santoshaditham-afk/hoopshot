import SwiftUI

struct ScoreSummaryView: View {
    let score: Int
    let shotsMade: Int
    let shotsTaken: Int
    let token: String
    let onDismiss: () -> Void

    @State private var submitting = false
    @State private var submitted = false
    @State private var submitError = ""

    var body: some View {
        ZStack {
            Color(red: 0.07, green: 0.1, blue: 0.18).ignoresSafeArea()

            VStack(spacing: 32) {
                Text("Game Over!").font(.largeTitle.bold()).foregroundColor(.white)

                VStack(spacing: 12) {
                    StatRow(label: "Score", value: "\(score)", accent: true)
                    StatRow(label: "Shots Made", value: "\(shotsMade)")
                    StatRow(label: "Shots Taken", value: "\(shotsTaken)")
                    if shotsTaken > 0 {
                        let pct = Int(Double(shotsMade) / Double(shotsTaken) * 100)
                        StatRow(label: "Accuracy", value: "\(pct)%")
                    }
                }
                .padding()
                .background(Color(white: 0.15))
                .cornerRadius(16)
                .padding(.horizontal, 32)

                if !submitError.isEmpty {
                    Text(submitError).foregroundColor(.red).font(.footnote)
                }

                VStack(spacing: 12) {
                    if !submitted {
                        Button(action: submitScore) {
                            if submitting {
                                ProgressView().tint(.white)
                            } else {
                                Text("Save Score").font(.headline).foregroundColor(.white).frame(maxWidth: .infinity)
                            }
                        }
                        .padding()
                        .background(Color.orange)
                        .cornerRadius(10)
                        .disabled(submitting)
                        .padding(.horizontal, 32)
                    } else {
                        Text("Score saved! ✓").foregroundColor(.green)
                    }

                    Button("Play Again", action: onDismiss)
                        .padding()
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .background(Color(white: 0.2))
                        .cornerRadius(10)
                        .padding(.horizontal, 32)
                }
            }
        }
    }

    private func submitScore() {
        submitting = true
        Task {
            do {
                let submission = ScoreSubmission(score: score, shotsTaken: shotsTaken, shotsMade: shotsMade)
                try await APIService.shared.submitScore(submission, token: token)
                await MainActor.run {
                    submitted = true
                    submitting = false
                }
            } catch {
                await MainActor.run {
                    submitError = error.localizedDescription
                    submitting = false
                }
            }
        }
    }
}

private struct StatRow: View {
    let label: String
    let value: String
    var accent = false

    var body: some View {
        HStack {
            Text(label).foregroundColor(.gray)
            Spacer()
            Text(value)
                .font(accent ? .title2.bold() : .body)
                .foregroundColor(accent ? .orange : .white)
        }
    }
}
