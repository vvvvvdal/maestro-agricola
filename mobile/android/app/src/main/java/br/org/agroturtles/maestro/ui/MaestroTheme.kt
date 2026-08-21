package br.org.agroturtles.maestro.ui

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Typography
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.Font
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import br.org.agroturtles.maestro.R

val MaestroYellow = Color(0xFFFCC931)
val MaestroGreen = Color(0xFF3C4C1E)
val MaestroBlue = Color(0xFF0F3C65)

// Tints de apoio derivados da paleta oficial, usados apenas como fundo de
// cartão. Não substituem nem recolorem os ativos da marca.
val MaestroSand = Color(0xFFF6F4E8)
val MaestroGreenSoft = Color(0xFFE7EEDA)
val MaestroYellowSoft = Color(0xFFFFF1CC)
val MaestroBlueSoft = Color(0xFFDDEAF5)
val MaestroOutline = Color(0xFFD9D6C4)

// Sinal de falha. Cor semântica de erro do Material 3, não cor de marca.
val MaestroRed = Color(0xFFB3261E)
val MaestroRedSoft = Color(0xFFF9DEDC)

private val LeagueSpartan = FontFamily(
    Font(R.font.league_spartan_regular, FontWeight.Normal),
    Font(R.font.league_spartan_medium, FontWeight.Medium),
    Font(R.font.league_spartan_semibold, FontWeight.SemiBold),
    Font(R.font.league_spartan_bold, FontWeight.Bold),
)

private val baseTypography = Typography()
private val MaestroTypography = Typography(
    displayLarge = baseTypography.displayLarge.copy(fontFamily = LeagueSpartan),
    displayMedium = baseTypography.displayMedium.copy(fontFamily = LeagueSpartan),
    displaySmall = baseTypography.displaySmall.copy(fontFamily = LeagueSpartan),
    headlineLarge = baseTypography.headlineLarge.copy(fontFamily = LeagueSpartan),
    headlineMedium = baseTypography.headlineMedium.copy(fontFamily = LeagueSpartan),
    headlineSmall = baseTypography.headlineSmall.copy(fontFamily = LeagueSpartan),
    titleLarge = baseTypography.titleLarge.copy(fontFamily = LeagueSpartan),
    titleMedium = baseTypography.titleMedium.copy(fontFamily = LeagueSpartan),
    titleSmall = baseTypography.titleSmall.copy(fontFamily = LeagueSpartan),
    bodyLarge = baseTypography.bodyLarge.copy(fontFamily = LeagueSpartan),
    bodyMedium = baseTypography.bodyMedium.copy(fontFamily = LeagueSpartan),
    bodySmall = baseTypography.bodySmall.copy(fontFamily = LeagueSpartan),
    labelLarge = baseTypography.labelLarge.copy(fontFamily = LeagueSpartan),
    labelMedium = baseTypography.labelMedium.copy(fontFamily = LeagueSpartan),
    labelSmall = baseTypography.labelSmall.copy(fontFamily = LeagueSpartan),
)

private val MaestroColors = lightColorScheme(
    primary = MaestroGreen,
    onPrimary = Color.White,
    primaryContainer = MaestroYellow,
    onPrimaryContainer = MaestroGreen,
    secondary = MaestroBlue,
    onSecondary = Color.White,
    secondaryContainer = Color(0xFFDDEAF5),
    onSecondaryContainer = MaestroBlue,
    tertiary = MaestroYellow,
    onTertiary = MaestroGreen,
    background = Color.White,
    onBackground = MaestroGreen,
    surface = Color.White,
    onSurface = MaestroGreen,
    surfaceVariant = MaestroSand,
    onSurfaceVariant = MaestroBlue,
    outline = Color(0xFF708054),
    error = MaestroRed,
    onError = Color.White,
    errorContainer = MaestroRedSoft,
    onErrorContainer = MaestroRed,
)

@Composable
fun MaestroTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = MaestroColors,
        typography = MaestroTypography,
        content = content,
    )
}
