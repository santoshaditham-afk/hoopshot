import Foundation

struct User: Codable {
    let id: Int
    let username: String
    let createdAt: String

    enum CodingKeys: String, CodingKey {
        case id, username
        case createdAt = "created_at"
    }
}

struct Score: Codable, Identifiable {
    let id: Int
    let score: Int
    let shotsTaken: Int
    let shotsMade: Int
    let createdAt: String
    let username: String?

    enum CodingKeys: String, CodingKey {
        case id, score, username
        case shotsTaken = "shots_taken"
        case shotsMade = "shots_made"
        case createdAt = "created_at"
    }
}

struct ScoreSubmission: Codable {
    let score: Int
    let shotsTaken: Int
    let shotsMade: Int

    enum CodingKeys: String, CodingKey {
        case score
        case shotsTaken = "shots_taken"
        case shotsMade = "shots_made"
    }
}

struct TokenResponse: Codable {
    let accessToken: String

    enum CodingKeys: String, CodingKey {
        case accessToken = "access_token"
    }
}

struct LoginRequest: Codable {
    let username: String
    let password: String
}
