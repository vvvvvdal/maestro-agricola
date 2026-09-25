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
import androidx.compose.material3.AlertDialog
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
import br.org.agroturtles.maestro.domain.RemoteTranscriptBlockReason

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
    resetEnabled: Boolean,
    remoteSessionConsentPrompt: Boolean,
    remoteBlockReason: RemoteTranscriptBlockReason?,
    onConfirmRemoteSession: () -> Unit,
    onDismissRemoteSession: () -> Unit,
    onDismissRemoteBlock: () -> Unit,
    onLook: () -> Unit,
    onListen: () -> Unit,
    onInterpret: () -> Unit,
    onReset: () -> Unit,
) {
    var toolsExpanded by rememberSaveable { mutableStateOf(frameSource == MOCK_FRAME_SOURCE) }

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

            val intentPresentation = intentPresentation(
                intent = result.intent,
                label = result.prediction?.label,
                confidence = result.prediction?.confidence,
                source = result.prediction?.source,
            )

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
                resetEnabled = resetEnabled,
                onLook = onLook,
                onListen = onListen,
                onReset = onReset,
            )

            ToolsPanel(
                expanded = toolsExpanded,
                onToggle = { toolsExpanded = !toolsExpanded },
                frameSource = frameSource,
                jevRemoteEnabled = jevRemoteEnabled,
                jevRemoteConsent = jevRemoteConsent,
                onJevRemoteEnabledChange = onJevRemoteEnabledChange,
                onJevRemoteConsentChange = onJevRemoteConsentChange,
                endpoint = endpoint,
                onEndpointChange = onEndpointChange,
                transcript = transcript,
                onTranscriptChange = onTranscriptChange,
                interactionPending = interactionPending,
                onInterpret = onInterpret,
            )
        }

        if (remoteSessionConsentPrompt) {
            RemoteSessionConsentDialog(
                onConfirm = onConfirmRemoteSession,
                onDismiss = onDismissRemoteSession,
            )
        }
        remoteBlockReason?.let { reason ->
            RemoteTranscriptBlockedDialog(
                reason = reason,
                onDismiss = onDismissRemoteBlock,
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
    val headline = statusHeadline(result.state, result.intent)
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
    resetEnabled: Boolean,
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
                text = "Inspecionar marcador",
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
                enabled = if (state == InteractionState.AWAITING_CONFIRMATION) enabled else resetEnabled,
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
    jevRemoteEnabled: Boolean,
    jevRemoteConsent: Boolean,
    onJevRemoteEnabledChange: (Boolean) -> Unit,
    onJevRemoteConsentChange: (Boolean) -> Unit,
    endpoint: String,
    onEndpointChange: (String) -> Unit,
    transcript: String,
    onTranscriptChange: (String) -> Unit,
    interactionPending: Boolean,
    onInterpret: () -> Unit,
) {
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
            Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
                Text(
                    text = "Ativar demonstração remota nesta sessão",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaestroBlue,
                )
                Text(
                    text = "Mostra um aviso antes de ativar.",
                    style = MaterialTheme.typography.labelSmall,
                    color = MaestroBlue.copy(alpha = 0.75f),
                )
            }
        }
    }
}

@Composable
private fun RemoteSessionConsentDialog(
    onConfirm: () -> Unit,
    onDismiss: () -> Unit,
) {
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("Ativar demonstração remota?") },
        text = {
            Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                Text(
                    text = "No modo Jev remoto, falas digitadas ou reconhecidas serão enviadas ao serviço externo apenas para classificar uma intenção.",
                    style = MaterialTheme.typography.bodyMedium,
                )
                Text(
                    text = "Não diga, escreva ou compartilhe nomes completos, e-mails, telefones, CPF/CNPJ, links, senhas, endereços ou qualquer informação pessoal ou confidencial.",
                    style = MaterialTheme.typography.bodyMedium,
                    fontWeight = FontWeight.SemiBold,
                    color = MaestroGreen,
                )
                Text(
                    text = "O app bloqueia alguns padrões evidentes, mas isso não substitui sua revisão. Desmarque para revogar a autorização ou selecione Local para classificar sem envio.",
                    style = MaterialTheme.typography.bodySmall,
                )
            }
        },
        confirmButton = {
            Button(onClick = onConfirm) {
                Text("Ativar Jev remoto")
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) {
                Text("Descartar")
            }
        },
    )
}

@Composable
private fun RemoteTranscriptBlockedDialog(
    reason: RemoteTranscriptBlockReason,
    onDismiss: () -> Unit,
) {
    val explanation = when (reason) {
        RemoteTranscriptBlockReason.PERSONAL_DATA ->
            "A fala contém um padrão de dado pessoal evidente e foi descartada localmente."
        RemoteTranscriptBlockReason.URL ->
            "A fala contém um endereço de internet e foi descartada localmente."
        RemoteTranscriptBlockReason.TOO_LONG ->
            "A fala excede o limite de uma frase curta de teste e foi descartada localmente."
        RemoteTranscriptBlockReason.OUTSIDE_REMOTE_SCOPE ->
            "A fala não corresponde ao escopo de comando do Jev remoto e foi descartada localmente."
    }

    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text("Fala não enviada ao Jev") },
        text = {
            Text(
                text = "$explanation Use Local para fazer uma nova interação fora da demonstração remota.",
                style = MaterialTheme.typography.bodyMedium,
            )
        },
        confirmButton = {
            Button(onClick = onDismiss) {
                Text("Entendi")
            }
        },
    )
}
