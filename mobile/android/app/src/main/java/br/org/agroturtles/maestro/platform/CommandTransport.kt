package br.org.agroturtles.maestro.platform

import br.org.agroturtles.maestro.domain.Command


fun interface CommandTransport {
    fun send(command: Command, completion: (accepted: Boolean, reason: String) -> Unit)
}
