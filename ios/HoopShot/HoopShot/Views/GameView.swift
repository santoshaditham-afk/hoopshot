import SwiftUI

// MARK: - Game state

private enum GamePhase {
    case idle, flying, scored, missed
}

// MARK: - GameView

struct GameView: View {
    let token: String

    // Timer
    @State private var timeLeft: Int = 30
    @State private var timer: Timer? = nil

    // Score tracking
    @State private var shotsTaken = 0
    @State private var shotsMade = 0
    @State private var score = 0

    // Ball physics
    @State private var ballPosition: CGPoint = .zero
    @State private var phase: GamePhase = .idle
    @State private var showSummary = false

    // Drag tracking
    @State private var dragStart: CGPoint = .zero
    @State private var isDragging = false

    // Feedback
    @State private var feedbackText = ""
    @State private var feedbackOpacity: Double = 0

    private let ballRadius: CGFloat = 22
    private let hoopHeight: CGFloat = 120  // from top

    var body: some View {
        GeometryReader { geo in
            let size = geo.size
            let hoopCenter = CGPoint(x: size.width / 2, y: hoopHeight + 20)
            let ballStart = CGPoint(x: size.width / 2, y: size.height - 100)

            ZStack {
                // Background
                LinearGradient(
                    colors: [Color(red: 0.07, green: 0.1, blue: 0.18), Color(red: 0.1, green: 0.15, blue: 0.25)],
                    startPoint: .top, endPoint: .bottom
                ).ignoresSafeArea()

                // Hoop
                HoopView(center: hoopCenter)

                // Ball
                Circle()
                    .fill(
                        RadialGradient(
                            colors: [Color.orange, Color(red: 0.8, green: 0.3, blue: 0)],
                            center: .topLeading, startRadius: 2, endRadius: ballRadius * 2
                        )
                    )
                    .frame(width: ballRadius * 2, height: ballRadius * 2)
                    .position(ballPosition)
                    .shadow(color: .orange.opacity(0.5), radius: 8)

                // HUD
                VStack {
                    HStack {
                        VStack(alignment: .leading, spacing: 4) {
                            Text("Score: \(score)").font(.title2.bold()).foregroundColor(.white)
                            Text("\(shotsMade)/\(shotsTaken) shots").font(.caption).foregroundColor(.gray)
                        }
                        Spacer()
                        TimerBadge(seconds: timeLeft)
                    }
                    .padding(.horizontal, 24)
                    .padding(.top, 12)
                    Spacer()

                    if phase == .idle {
                        Text("Swipe up to shoot!")
                            .font(.headline)
                            .foregroundColor(.white.opacity(0.6))
                            .padding(.bottom, 140)
                    }
                }

                // Feedback
                Text(feedbackText)
                    .font(.system(size: 42, weight: .black))
                    .foregroundColor(feedbackText == "MISS" ? .red : .green)
                    .opacity(feedbackOpacity)
                    .position(x: size.width / 2, y: size.height / 2)
            }
            .onAppear {
                ballPosition = ballStart
                startTimer()
            }
            .onDisappear { timer?.invalidate() }
            .gesture(
                DragGesture(minimumDistance: 10)
                    .onChanged { value in
                        if phase == .idle {
                            isDragging = true
                            dragStart = value.startLocation
                        }
                    }
                    .onEnded { value in
                        guard phase == .idle, isDragging else { return }
                        isDragging = false
                        let dy = dragStart.y - value.location.y  // positive = upward
                        let dx = value.location.x - dragStart.x
                        guard dy > 20 else { return }  // must swipe up
                        shoot(from: ballStart, to: hoopCenter, dx: dx, dy: dy, size: size)
                    }
            )
            .sheet(isPresented: $showSummary) {
                ScoreSummaryView(
                    score: score,
                    shotsMade: shotsMade,
                    shotsTaken: shotsTaken,
                    token: token
                ) {
                    showSummary = false
                    resetGame(ballStart: ballStart)
                }
            }
        }
    }

    // MARK: - Shooting

    private func shoot(from start: CGPoint, to hoop: CGPoint, dx: CGFloat, dy: CGFloat, size: CGSize) {
        guard phase == .idle else { return }
        phase = .flying
        shotsTaken += 1

        // Determine if this shot scores based on swipe accuracy
        let swipeAngle = atan2(dx, dy)            // deviation from straight-up
        let powerRatio = min(dy / 300, 1.0)       // 0–1
        let made = abs(swipeAngle) < 0.35 && powerRatio > 0.4  // generous for fun

        // Animate ball along arc
        let duration: Double = 0.7
        let controlX = start.x + dx * 0.3
        let controlY = min(start.y, hoop.y) - 80

        let steps = 60
        let stepDuration = duration / Double(steps)
        var step = 0

        Timer.scheduledTimer(withTimeInterval: stepDuration, repeats: true) { t in
            let progress = Double(step) / Double(steps)
            let t0 = 1 - progress

            // Quadratic bezier
            let bx = t0 * t0 * start.x + 2 * t0 * progress * controlX + progress * progress * hoop.x
            let by = t0 * t0 * start.y + 2 * t0 * progress * controlY + progress * progress * hoop.y

            ballPosition = CGPoint(x: bx, y: by)
            step += 1

            if step >= steps {
                t.invalidate()
                resolveShot(made: made, ballStart: CGPoint(x: size.width / 2, y: size.height - 100))
            }
        }
    }

    private func resolveShot(made: Bool, ballStart: CGPoint) {
        if made {
            shotsMade += 1
            score += 2
            showFeedback("NICE!", color: .green)
        } else {
            showFeedback("MISS", color: .red)
        }

        DispatchQueue.main.asyncAfter(deadline: .now() + 0.6) {
            withAnimation(.easeOut(duration: 0.3)) {
                ballPosition = ballStart
            }
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) {
                phase = .idle
            }
        }
    }

    private func showFeedback(_ text: String, color: Color) {
        feedbackText = text
        withAnimation(.easeIn(duration: 0.1)) { feedbackOpacity = 1 }
        withAnimation(.easeOut(duration: 0.4).delay(0.5)) { feedbackOpacity = 0 }
    }

    // MARK: - Timer

    private func startTimer() {
        timeLeft = 30
        timer?.invalidate()
        timer = Timer.scheduledTimer(withTimeInterval: 1, repeats: true) { _ in
            if timeLeft > 0 {
                timeLeft -= 1
            } else {
                timer?.invalidate()
                showSummary = true
            }
        }
    }

    private func resetGame(ballStart: CGPoint) {
        score = 0
        shotsTaken = 0
        shotsMade = 0
        ballPosition = ballStart
        phase = .idle
        startTimer()
    }
}

// MARK: - Supporting Views

private struct HoopView: View {
    let center: CGPoint

    var body: some View {
        ZStack {
            // Backboard
            Rectangle()
                .fill(Color.white.opacity(0.15))
                .frame(width: 90, height: 60)
                .position(x: center.x, y: center.y - 50)
                .cornerRadius(4)

            // Rim
            Capsule()
                .fill(Color.orange)
                .frame(width: 80, height: 8)
                .position(x: center.x, y: center.y)

            // Net (simplified lines)
            ForEach(0..<5) { i in
                let offset = CGFloat(i - 2) * 12
                Rectangle()
                    .fill(Color.white.opacity(0.4))
                    .frame(width: 1, height: 30)
                    .position(x: center.x + offset, y: center.y + 20)
            }
        }
    }
}

private struct TimerBadge: View {
    let seconds: Int

    var body: some View {
        Text("\(seconds)s")
            .font(.title2.bold().monospacedDigit())
            .foregroundColor(seconds <= 10 ? .red : .white)
            .padding(.horizontal, 12)
            .padding(.vertical, 6)
            .background(Color(white: 0.2))
            .cornerRadius(20)
    }
}
