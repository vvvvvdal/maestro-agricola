package br.org.agroturtles.maestro.domain

private const val DEFAULT_OPERATION_STATUS_MAX_POLLS = 60
private const val DOCK_OPERATION_STATUS_MAX_POLLS = 120

fun operationStatusMaxPolls(command: Command): Int =
    if (command.intent == "DOCK") DOCK_OPERATION_STATUS_MAX_POLLS
    else DEFAULT_OPERATION_STATUS_MAX_POLLS
