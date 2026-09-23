package br.org.agroturtles.maestro.ui

import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.IntrinsicSize
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.RowScope
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.imePadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.systemBarsPadding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.Checkbox
import androidx.compose.material3.FilterChip
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import br.org.agroturtles.maestro.R
import br.org.agroturtles.maestro.domain.InteractionEngine
import br.org.agroturtles.maestro.domain.InteractionResult
import br.org.agroturtles.maestro.domain.InteractionState
import br.org.agroturtles.maestro.domain.JevChoiceAnswer

private const val MOCK_FRAME_SOURCE = "mock"

private val CardShape = RoundedCornerShape(20.dp)
private val ChipShape = RoundedCornerShape(50)

private data class ToneColors(val container: Color, val content: Color)

private fun toneColors(tone: Tone): ToneColors = when (tone) {
    Tone.NEUTRAL -> ToneColors(MaestroSand, MaestroGreen)
    Tone.INFO -> ToneColors(MaestroBlueSoft, MaestroBlue)
    Tone.ATTENTION -> ToneColors(MaestroYellowSoft, MaestroGreen)
    Tone.SUCCESS -> ToneColors(MaestroGreenSoft, MaestroGreen)
    Tone.DANGER -> ToneColors(MaestroRedSoft, MaestroRed)
}

/**
 * Tela única da demonstração.
 *
 * A ordem de leitura acompanha a jornada: marca, estado atual, trilha da
 * jornada, fatos destacados (alvo, intenção, robô) e só então as ações. O que
 * existe apenas para diagnóstico fica em "Ajustes de teste".
 *
 * O painel começa aberto no flavor `mock`, que existe para desenvolvimento e
 * teste sem óculos, e fechado no `dat`, que é o build da demonstração.
 */
@Composable
fun MaestroScreen(
    result: InteractionResult,
    robot: RobotPresentation,
    frameSource: String,
    jevScenarios: List<JevChoiceAnswer>,
    jevDiagnostic: JevChoiceAnswer?,
    jevRemoteEnabled: Boolean,
    jevRemoteConsent: Boolean,
    onJevRemoteEnabledChange: (Boolean) -> Unit,
    onJevRemoteConsentChange: (Boolean) -> Unit,
    endpoint: String,
    onEndpointChange: (String) -> Unit,
    transcript: String,
    onTranscriptChange: (String) -> Unit,
    secondsToExpire: Int,
    interactionPending: Boolean,
    onLook: () -> Unit,
    onListen: () -> Unit,
    onInterpret: () -> Unit,
    onReset: () -> Unit,
) {
    var toolsExpanded by rememberSaveable { mutableStateOf(frameSource == MOCK_FRAME_SOURCE) }
    var selectedJevChoice by rememberSaveable { mutableStateOf<String?>(null) }
    val selectedJevScenario = jevScenarios.firstOrNull { it.choice == selectedJevChoice }

    Surface(
        modifier = Modifier.fillMaxSize(),
        color = MaterialTheme.colorScheme.background,
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .systemBarsPadding()
                .imePadding()
                .verticalScroll(rememberScrollState())
                .padding(horizontal = 20.dp, vertical = 16.dp),
            verticalArrangement = Arrangement.spacedBy(14.dp),
        ) {
            Header(frameSource = frameSource, endpoint = endpoint)

            StatusCard(result = result, secondsToExpire = secondsToExpire)

            JourneyStrip(steps = journeySteps(result.state, result.intent))

            val localIntentPresentation = intentPresentation(
                intent = result.intent,
                label = result.prediction?.label,
                confidence = result.prediction?.confidence,
                source = result.prediction?.source,
            )
            val intentPresentation = jevScenarioIntentPresentation(selectedJevScenario)
                ?: localIntentPresentation

            Row(
                modifier = Modifier.height(IntrinsicSize.Min),
                horizontalArrangement = Arrangement.spacedBy(12.dp),
            ) {
                FactCard(
                    title = "ALVO DETECTADO",
                    value = targetValue(result.intent, result.targetId),
                    detail = targetDetail(result.intent, result.targetId, result.targetSource),
                    tone = if (result.targetId == null) Tone.NEUTRAL else Tone.INFO,
                    modifier = Modifier
                        .weight(1f)
                        .fillMaxHeight(),
                )
                FactCard(
                    title = "INTENÇÃO",
                    value = intentPresentation.value,
                    detail = intentPresentation.detail,
                    tone = intentPresentation.tone,
                    modifier = Modifier
                        .weight(1f)
                        .fillMaxHeight(),
                )
            }

            FactCard(
                title = "ROBÔ · ÚLTIMO COMANDO ACEITO",
                value = robot.title,
                detail = robot.detail,
                tone = robot.tone,
                modifier = Modifier.fillMaxWidth(),
            )

            Actions(
                state = result.state,
                enabled = !interactionPending,
                onLook = onLook,
                onListen = onListen,
                onReset = onReset,
            )

            ToolsPanel(
                expanded = toolsExpanded,
                onToggle = { toolsExpanded = !toolsExpanded },
                frameSource = frameSource,
                jevScenarios = jevScenarios,
                jevDiagnostic = jevDiagnostic,
                jevRemoteEnabled = jevRemoteEnabled,
                jevRemoteConsent = jevRemoteConsent,
                onJevRemoteEnabledChange = onJevRemoteEnabledChange,
                onJevRemoteConsentChange = onJevRemoteConsentChange,
                selectedJevChoice = selectedJevChoice,
                onJevScenarioSelected = { selectedJevChoice = it },
                endpoint = endpoint,
                onEndpointChange = onEndpointChange,
                transcript = transcript,
                onTranscriptChange = onTranscriptChange,
                interactionPending = interactionPending,
                onInterpret = onInterpret,
            )
        }
    }
}

@Composable
private fun Header(frameSource: String, endpoint: String) {
    Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
        BoxWithConstraints(
            modifier = Modifier
                .fillMaxWidth()
                .height(88.dp),
            contentAlignment = Alignment.Center,
        ) {
            val logoWidth = if (maxWidth > 480.dp) 480.dp else maxWidth
            Image(
                painter = painterResource(R.drawable.maestro_logo_horizontal),
                contentDescription = "Maestro Agrícola por AgroTurtles",
                contentScale = ContentScale.Crop,
                modifier = Modifier
                    .width(logoWidth)
                    .fillMaxHeight(),
            )
        }
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            Chip(text = "câmera: $frameSource")
            Chip(text = endpoint, modifier = Modifier.weight(1f, fill = false))
        }
    }
}

@Composable
private fun Chip(
    text: String,
    tone: Tone = Tone.NEUTRAL,
    modifier: Modifier = Modifier,
) {
    val colors = toneColors(tone)
    Surface(color = colors.container, shape = ChipShape, modifier = modifier) {
        Text(
            text = text,
            modifier = Modifier.padding(horizontal = 12.dp, vertical = 5.dp),
            style = MaterialTheme.typography.labelMedium,
            color = colors.content,
            maxLines = 1,
            overflow = TextOverflow.Ellipsis,
        )
    }
}

@Composable
private fun StatusCard(result: InteractionResult, secondsToExpire: Int) {
    val headline = statusHeadline(result.state)
    val colors = toneColors(headline.tone)

    Surface(
        color = colors.container,
        shape = CardShape,
        modifier = Modifier.fillMaxWidth(),
    ) {
        Column(
            modifier = Modifier.padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(6.dp),
        ) {
            Text(
                text = headline.label,
                style = MaterialTheme.typography.labelMedium,
                fontWeight = FontWeight.Bold,
                color = colors.content.copy(alpha = 0.7f),
            )
            Text(
                text = headline.title,
                style = MaterialTheme.typography.headlineSmall,
                fontWeight = FontWeight.Bold,
                color = colors.content,
            )
            Text(
                text = result.message,
                style = MaterialTheme.typography.bodyLarge,
                color = colors.content.copy(alpha = 0.85f),
            )

            if (result.state == InteractionState.AWAITING_CONFIRMATION) {
                Spacer(modifier = Modifier.height(6.dp))
                Text(
                    text = "Diga \"sim\" para confirmar ou \"cancelar\" para abortar.",
                    style = MaterialTheme.typography.bodyMedium,
                    fontWeight = FontWeight.SemiBold,
                    color = colors.content,
                )
                Spacer(modifier = Modifier.height(4.dp))
                CountdownBar(
                    secondsToExpire = secondsToExpire,
                    color = colors.content,
                )
                Text(
                    text = "expira em ${secondsToExpire}s · sem confirmação nada é enviado",
                    style = MaterialTheme.typography.labelMedium,
                    color = colors.content.copy(alpha = 0.75f),
                )
            }
        }
    }
}

@Composable
private fun CountdownBar(secondsToExpire: Int, color: Color) {
    val total = InteractionEngine.CONFIRMATION_TIMEOUT_SECONDS.toFloat()
    val fraction = (secondsToExpire.toFloat() / total).coerceIn(0f, 1f)

    Box(
        modifier = Modifier
            .fillMaxWidth()
            .height(8.dp)
            .background(color.copy(alpha = 0.18f), ChipShape),
    ) {
        Box(
            modifier = Modifier
                .fillMaxWidth(fraction)
                .height(8.dp)
                .background(color, ChipShape),
        )
    }
}

@Composable
private fun JourneyStrip(steps: List<JourneyStep>) {
    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
        steps.forEach { step ->
            Column(
                modifier = Modifier.weight(1f),
                verticalArrangement = Arrangement.spacedBy(6.dp),
            ) {
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(6.dp)
                        .background(stepColor(step.status), ChipShape),
                )
                Text(
                    text = step.label,
                    style = MaterialTheme.typography.labelMedium,
                    fontWeight = if (step.status == StepStatus.ACTIVE) {
                        FontWeight.Bold
                    } else {
                        FontWeight.Normal
                    },
                    color = stepLabelColor(step.status),
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis,
                )
            }
        }
    }
}

private fun stepColor(status: StepStatus): Color = when (status) {
    StepStatus.DONE -> MaestroGreen
    StepStatus.ACTIVE -> MaestroYellow
    StepStatus.BLOCKED -> MaestroRed
    StepStatus.SKIPPED -> MaestroOutline
    StepStatus.PENDING -> MaestroOutline
}

private fun stepLabelColor(status: StepStatus): Color = when (status) {
    StepStatus.DONE -> MaestroGreen
    StepStatus.ACTIVE -> MaestroGreen
    StepStatus.BLOCKED -> MaestroRed
    StepStatus.SKIPPED -> MaestroBlue.copy(alpha = 0.5f)
    StepStatus.PENDING -> MaestroBlue.copy(alpha = 0.5f)
}

@Composable
private fun FactCard(
    title: String,
    value: String,
    detail: String,
    tone: Tone,
    modifier: Modifier = Modifier,
) {
    val colors = toneColors(tone)
    Surface(
        color = colors.container,
        shape = CardShape,
        modifier = modifier.semantics(mergeDescendants = true) {
            contentDescription = factCardContentDescription(title, value, detail)
        },
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(4.dp),
        ) {
            Text(
                text = title,
                style = MaterialTheme.typography.labelSmall,
                fontWeight = FontWeight.Bold,
                color = colors.content.copy(alpha = 0.7f),
            )
            Text(
                text = value,
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
                color = colors.content,
            )
            Text(
                text = detail,
                style = MaterialTheme.typography.bodySmall,
                color = colors.content.copy(alpha = 0.8f),
            )
        }
    }
}

@Composable
private fun Actions(
    state: InteractionState,
    enabled: Boolean,
    onLook: () -> Unit,
    onListen: () -> Unit,
    onReset: () -> Unit,
) {
    Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
        Button(
            onClick = onListen,
            enabled = enabled,
            modifier = Modifier
                .fillMaxWidth()
                .height(60.dp),
            shape = CardShape,
        ) {
            Text(
                text = if (state == InteractionState.AWAITING_CONFIRMATION) {
                    "Falar para confirmar"
                } else {
                    "Falar"
                },
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
                fontSize = 18.sp,
            )
        }
        Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
            SecondaryAction(
                text = "Olhar para o alvo",
                onClick = onLook,
                enabled = enabled,
            )
            SecondaryAction(
                text = if (state == InteractionState.AWAITING_CONFIRMATION) {
                    "Cancelar"
                } else {
                    "Reiniciar"
                },
                onClick = onReset,
                enabled = enabled,
            )
        }
    }
}

@Composable
private fun RowScope.SecondaryAction(text: String, onClick: () -> Unit, enabled: Boolean = true) {
    OutlinedButton(
        onClick = onClick,
        enabled = enabled,
        modifier = Modifier
            .weight(1f)
            .height(48.dp),
        shape = CardShape,
    ) {
        Text(text = text, maxLines = 1, overflow = TextOverflow.Ellipsis)
    }
}

@Composable
private fun ToolsPanel(
    expanded: Boolean,
    onToggle: () -> Unit,
    frameSource: String,
    jevScenarios: List<JevChoiceAnswer>,
    jevDiagnostic: JevChoiceAnswer?,
    jevRemoteEnabled: Boolean,
    jevRemoteConsent: Boolean,
    onJevRemoteEnabledChange: (Boolean) -> Unit,
    onJevRemoteConsentChange: (Boolean) -> Unit,
    selectedJevChoice: String?,
    onJevScenarioSelected: (String?) -> Unit,
    endpoint: String,
    onEndpointChange: (String) -> Unit,
    transcript: String,
    onTranscriptChange: (String) -> Unit,
    interactionPending: Boolean,
    onInterpret: () -> Unit,
) {
    val diagnostic = jevDiagnosticPresentation(jevDiagnostic)
    val showsJevScenarios = shouldShowJevScenarios(frameSource, jevScenarios)
    val showsJevDiagnostics = shouldShowJevDiagnostics(
        frameSource = frameSource,
        diagnostic = diagnostic,
        selectedChoice = selectedJevChoice,
    )
    var diagnosticsExpanded by rememberSaveable { mutableStateOf(false) }

    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        TextButton(onClick = onToggle, modifier = Modifier.align(Alignment.Start)) {
            Text(
                text = if (expanded) "Ocultar ajustes de teste" else "Ajustes de teste",
                style = MaterialTheme.typography.labelLarge,
            )
        }

        if (expanded) {
            Surface(color = MaestroSand, shape = CardShape, modifier = Modifier.fillMaxWidth()) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp),
                ) {
                    OutlinedTextField(
                        value = endpoint,
                        onValueChange = onEndpointChange,
                        label = { Text("Bridge WebSocket") },
                        supportingText = { Text("Em celular físico, use o IP do computador") },
                        singleLine = true,
                        enabled = !interactionPending,
                        modifier = Modifier.fillMaxWidth(),
                    )
                    OutlinedTextField(
                        value = transcript,
                        onValueChange = onTranscriptChange,
                        label = { Text("Transcrição digitada") },
                        supportingText = { Text("Contingência quando o microfone falhar") },
                        singleLine = true,
                        keyboardOptions = KeyboardOptions(imeAction = ImeAction.Send),
                        keyboardActions = KeyboardActions(onSend = {
                            if (!interactionPending) onInterpret()
                        }),
                        enabled = !interactionPending,
                        modifier = Modifier.fillMaxWidth(),
                    )
                    Button(
                        onClick = onInterpret,
                        enabled = !interactionPending,
                        modifier = Modifier.fillMaxWidth(),
                        shape = CardShape,
                    ) {
                        Text("Interpretar texto")
                    }
                    Text(
                        text = "Fonte de frame: $frameSource · modelo e alvos lidos dos assets versionados",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaestroBlue,
                    )
                    if (frameSource == MOCK_FRAME_SOURCE) {
                        JevRemoteSelector(
                            enabled = jevRemoteEnabled,
                            consent = jevRemoteConsent,
                            interactionsEnabled = !interactionPending,
                            onEnabledChange = onJevRemoteEnabledChange,
                            onConsentChange = onJevRemoteConsentChange,
                        )
                    }
                    if (showsJevScenarios && !jevRemoteEnabled) {
                        JevScenarioSelector(
                            scenarios = jevScenarios,
                            selectedChoice = selectedJevChoice,
                            onSelected = onJevScenarioSelected,
                        )
                        if (showsJevDiagnostics) {
                            JevDiagnostics(
                                diagnostic = requireNotNull(diagnostic),
                                expanded = diagnosticsExpanded,
                                onToggle = { diagnosticsExpanded = !diagnosticsExpanded },
                            )
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun JevRemoteSelector(
    enabled: Boolean,
    consent: Boolean,
    interactionsEnabled: Boolean,
    onEnabledChange: (Boolean) -> Unit,
    onConsentChange: (Boolean) -> Unit,
) {
    Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
        Text(
            text = "Fonte da intencao",
            style = MaterialTheme.typography.labelLarge,
            color = MaestroBlue,
        )
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            FilterChip(
                selected = !enabled,
                onClick = { onEnabledChange(false) },
                enabled = interactionsEnabled,
                label = { Text("Local") },
            )
            FilterChip(
                selected = enabled,
                onClick = { onEnabledChange(true) },
                enabled = interactionsEnabled && consent,
                label = { Text("Jev remoto") },
            )
        }
        Row(verticalAlignment = Alignment.CenterVertically) {
            Checkbox(
                checked = consent,
                onCheckedChange = onConsentChange,
                enabled = interactionsEnabled,
            )
            Text(
                text = "Fala de teste sem dados pessoais",
                style = MaterialTheme.typography.bodySmall,
                color = MaestroBlue,
            )
        }
    }
}

@Composable
private fun JevScenarioSelector(
    scenarios: List<JevChoiceAnswer>,
    selectedChoice: String?,
    onSelected: (String?) -> Unit,
) {
    Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
        Text(
            text = "Cenário Jev · somente mock",
            style = MaterialTheme.typography.labelLarge,
            color = MaestroBlue,
        )
        Text(
            text = "Altera somente o cartão INTENÇÃO · sem rede ou comando",
            style = MaterialTheme.typography.bodySmall,
            color = MaestroBlue,
        )
        FilterChip(
            selected = selectedChoice == null,
            onClick = { onSelected(null) },
            label = { Text("Baseline local") },
        )
        scenarios.forEach { scenario ->
            FilterChip(
                selected = selectedChoice == scenario.choice,
                onClick = { onSelected(scenario.choice) },
                label = { Text(jevScenarioLabel(scenario.choice)) },
            )
        }
    }
}

@Composable
private fun JevDiagnostics(
    diagnostic: JevDiagnosticPresentation,
    expanded: Boolean,
    onToggle: () -> Unit,
) {
    Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
        TextButton(onClick = onToggle, modifier = Modifier.align(Alignment.Start)) {
            Text(
                text = if (expanded) "Ocultar diagnóstico Jev" else "Ver diagnóstico Jev",
                style = MaterialTheme.typography.labelLarge,
            )
        }

        if (expanded) {
            Text(
                text = "Fixture local do mock · não participa da decisão operacional",
                style = MaterialTheme.typography.bodySmall,
                color = MaestroBlue,
            )
            Text(
                text = "Escolha: ${diagnostic.choice} · probabilidade: ${diagnostic.selectedProbability}",
                style = MaterialTheme.typography.bodySmall,
                fontWeight = FontWeight.SemiBold,
                color = MaestroBlue,
            )
            Text(
                text = "Confidence do Jev: ${diagnostic.confidence}",
                style = MaterialTheme.typography.bodySmall,
                color = MaestroBlue,
            )
            diagnostic.rows.forEach { row ->
                Row(modifier = Modifier.fillMaxWidth()) {
                    Text(
                        text = row.label,
                        style = MaterialTheme.typography.labelSmall,
                        color = MaestroBlue,
                        modifier = Modifier.weight(1f),
                    )
                    Text(
                        text = row.probability,
                        style = MaterialTheme.typography.labelSmall,
                        fontWeight = FontWeight.SemiBold,
                        color = MaestroBlue,
                    )
                }
            }
        }
    }
}
