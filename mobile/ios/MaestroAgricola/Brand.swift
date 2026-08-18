import SwiftUI

enum MaestroBrand {
    static let yellow = Color(red: 252 / 255, green: 201 / 255, blue: 49 / 255)
    static let green = Color(red: 60 / 255, green: 76 / 255, blue: 30 / 255)
    static let blue = Color(red: 15 / 255, green: 60 / 255, blue: 101 / 255)

    enum Weight {
        case regular
        case medium
        case semibold
        case bold

        var postScriptName: String {
            switch self {
            case .regular: "LeagueSpartan-Regular"
            case .medium: "LeagueSpartan-Medium"
            case .semibold: "LeagueSpartan-SemiBold"
            case .bold: "LeagueSpartan-Bold"
            }
        }
    }

    static func font(
        _ textStyle: Font.TextStyle,
        size: CGFloat,
        weight: Weight = .regular
    ) -> Font {
        .custom(weight.postScriptName, size: size, relativeTo: textStyle)
    }
}
