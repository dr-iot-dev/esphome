"""Audio Recorder component for ESPHome."""

from esphome import automation
from esphome.automation import register_action, register_condition
import esphome.codegen as cg
from esphome.components import media_player, microphone, speaker
import esphome.config_validation as cv
from esphome.const import (
    CONF_ID,
    CONF_MEDIA_PLAYER,
    CONF_MICROPHONE,
    CONF_ON_CLIENT_CONNECTED,
    CONF_ON_CLIENT_DISCONNECTED,
    CONF_ON_ERROR,
    CONF_ON_IDLE,
    CONF_SPEAKER,
)

AUTO_LOAD = ["mqtt"]
DEPENDENCIES = ["api", "microphone"]

CODEOWNERS = ["@dr-iot-dev"]

CONF_ON_END = "on_end"
CONF_ON_INTENT_END = "on_intent_end"
CONF_ON_INTENT_START = "on_intent_start"
CONF_ON_LISTENING = "on_listening"
CONF_ON_START = "on_start"


CONF_AUTO_GAIN = "auto_gain"
CONF_NOISE_SUPPRESSION_LEVEL = "noise_suppression_level"
CONF_VOLUME_MULTIPLIER = "volume_multiplier"

CONF_ON_TIMER_STARTED = "on_timer_started"
CONF_ON_TIMER_UPDATED = "on_timer_updated"
CONF_ON_TIMER_CANCELLED = "on_timer_cancelled"
CONF_ON_TIMER_FINISHED = "on_timer_finished"
CONF_ON_TIMER_TICK = "on_timer_tick"


audio_recorder_ns = cg.esphome_ns.namespace("audio_recorder")
AudioRecorder = audio_recorder_ns.class_("AudioRecorder", cg.Component)

StartAction = audio_recorder_ns.class_(
    "StartAction", automation.Action, cg.Parented.template(AudioRecorder)
)
StartContinuousAction = audio_recorder_ns.class_(
    "StartContinuousAction", automation.Action, cg.Parented.template(AudioRecorder)
)
StopAction = audio_recorder_ns.class_(
    "StopAction", automation.Action, cg.Parented.template(AudioRecorder)
)
IsRunningCondition = audio_recorder_ns.class_(
    "IsRunningCondition", automation.Condition, cg.Parented.template(AudioRecorder)
)
ConnectedCondition = audio_recorder_ns.class_(
    "ConnectedCondition", automation.Condition, cg.Parented.template(AudioRecorder)
)

Timer = audio_recorder_ns.struct("Timer")

CONFIG_SCHEMA = cv.All(
    cv.Schema(
        {
            cv.GenerateID(): cv.declare_id(AudioRecorder),
            cv.GenerateID(CONF_MICROPHONE): cv.use_id(microphone.Microphone),
            cv.Exclusive(CONF_SPEAKER, "output"): cv.use_id(speaker.Speaker),
            cv.Exclusive(CONF_MEDIA_PLAYER, "output"): cv.use_id(
                media_player.MediaPlayer
            ),
            cv.Optional(CONF_NOISE_SUPPRESSION_LEVEL, default=0): cv.int_range(0, 4),
            cv.Optional(CONF_AUTO_GAIN, default="0dBFS"): cv.All(
                cv.float_with_unit("decibel full scale", "(dBFS|dbfs|DBFS)"),
                cv.int_range(0, 31),
            ),
            cv.Optional(CONF_VOLUME_MULTIPLIER, default=1.0): cv.float_range(
                min=0.0, min_included=False
            ),
            cv.Optional(CONF_ON_LISTENING): automation.validate_automation(single=True),
            cv.Optional(CONF_ON_START): automation.validate_automation(single=True),
            cv.Optional(CONF_ON_END): automation.validate_automation(single=True),
            cv.Optional(CONF_ON_ERROR): automation.validate_automation(single=True),
            cv.Optional(CONF_ON_CLIENT_CONNECTED): automation.validate_automation(
                single=True
            ),
            cv.Optional(CONF_ON_CLIENT_DISCONNECTED): automation.validate_automation(
                single=True
            ),
            cv.Optional(CONF_ON_INTENT_START): automation.validate_automation(
                single=True
            ),
            cv.Optional(CONF_ON_INTENT_END): automation.validate_automation(
                single=True
            ),
            cv.Optional(CONF_ON_IDLE): automation.validate_automation(single=True),
            cv.Optional(CONF_ON_TIMER_STARTED): automation.validate_automation(
                single=True
            ),
            cv.Optional(CONF_ON_TIMER_UPDATED): automation.validate_automation(
                single=True
            ),
            cv.Optional(CONF_ON_TIMER_CANCELLED): automation.validate_automation(
                single=True
            ),
            cv.Optional(CONF_ON_TIMER_FINISHED): automation.validate_automation(
                single=True
            ),
            cv.Optional(CONF_ON_TIMER_TICK): automation.validate_automation(
                single=True
            ),
        }
    ).extend(cv.COMPONENT_SCHEMA),
)


async def to_code(config):
    """Convert configuration to code."""
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)

    mic = await cg.get_variable(config[CONF_MICROPHONE])
    cg.add(var.set_microphone(mic))

    if CONF_SPEAKER in config:
        spkr = await cg.get_variable(config[CONF_SPEAKER])
        cg.add(var.set_speaker(spkr))

    if CONF_MEDIA_PLAYER in config:
        mp = await cg.get_variable(config[CONF_MEDIA_PLAYER])
        cg.add(var.set_media_player(mp))

    cg.add(var.set_noise_suppression_level(config[CONF_NOISE_SUPPRESSION_LEVEL]))
    cg.add(var.set_auto_gain(config[CONF_AUTO_GAIN]))
    cg.add(var.set_volume_multiplier(config[CONF_VOLUME_MULTIPLIER]))

    if CONF_ON_LISTENING in config:
        await automation.build_automation(
            var.get_listening_trigger(), [], config[CONF_ON_LISTENING]
        )

    if CONF_ON_START in config:
        await automation.build_automation(
            var.get_start_trigger(), [], config[CONF_ON_START]
        )

    if CONF_ON_END in config:
        await automation.build_automation(
            var.get_end_trigger(), [], config[CONF_ON_END]
        )

    if CONF_ON_ERROR in config:
        await automation.build_automation(
            var.get_error_trigger(),
            [(cg.std_string, "code"), (cg.std_string, "message")],
            config[CONF_ON_ERROR],
        )

    if CONF_ON_CLIENT_CONNECTED in config:
        await automation.build_automation(
            var.get_client_connected_trigger(),
            [],
            config[CONF_ON_CLIENT_CONNECTED],
        )

    if CONF_ON_CLIENT_DISCONNECTED in config:
        await automation.build_automation(
            var.get_client_disconnected_trigger(),
            [],
            config[CONF_ON_CLIENT_DISCONNECTED],
        )

    if CONF_ON_IDLE in config:
        await automation.build_automation(
            var.get_idle_trigger(),
            [],
            config[CONF_ON_IDLE],
        )

    has_timers = False
    # if on_timer_started := config.get(CONF_ON_TIMER_STARTED):
    #     await automation.build_automation(
    #         var.get_timer_started_trigger(),
    #         [(Timer, "timer")],
    #         on_timer_started,
    #     )
    #     has_timers = True

    # if on_timer_updated := config.get(CONF_ON_TIMER_UPDATED):
    #     await automation.build_automation(
    #         var.get_timer_updated_trigger(),
    #         [(Timer, "timer")],
    #         on_timer_updated,
    #     )
    #     has_timers = True

    # if on_timer_cancelled := config.get(CONF_ON_TIMER_CANCELLED):
    #     await automation.build_automation(
    #         var.get_timer_cancelled_trigger(),
    #         [(Timer, "timer")],
    #         on_timer_cancelled,
    #     )
    #     has_timers = True

    # if on_timer_finished := config.get(CONF_ON_TIMER_FINISHED):
    #     await automation.build_automation(
    #         var.get_timer_finished_trigger(),
    #         [(Timer, "timer")],
    #         on_timer_finished,
    #     )
    #     has_timers = True

    # if on_timer_tick := config.get(CONF_ON_TIMER_TICK):
    #     await automation.build_automation(
    #         var.get_timer_tick_trigger(),
    #         [(cg.std_vector.template(Timer), "timers")],
    #         on_timer_tick,
    #     )
    #     has_timers = True

    cg.add(var.set_has_timers(has_timers))

    cg.add_define("USE_audio_recorder")


audio_recorder_ACTION_SCHEMA = cv.Schema({cv.GenerateID(): cv.use_id(AudioRecorder)})


@register_action(
    "audio_recorder.start_continuous",
    StartContinuousAction,
    audio_recorder_ACTION_SCHEMA,
)
@register_action("audio_recorder.stop", StopAction, audio_recorder_ACTION_SCHEMA)
async def audio_recorder_stop_to_code(config, action_id, template_arg, _args):
    """Convert configuration to code."""
    var = cg.new_Pvariable(action_id, template_arg)
    await cg.register_parented(var, config[CONF_ID])
    return var


@register_condition(
    "audio_recorder.is_running", IsRunningCondition, audio_recorder_ACTION_SCHEMA
)
async def audio_recorder_is_running_to_code(config, condition_id, template_arg, _args):
    """Convert configuration to code."""
    var = cg.new_Pvariable(condition_id, template_arg)
    await cg.register_parented(var, config[CONF_ID])
    return var


@register_condition(
    "audio_recorder.connected", ConnectedCondition, audio_recorder_ACTION_SCHEMA
)
async def audio_recorder_connected_to_code(config, condition_id, template_arg, _args):
    """Convert configuration to code."""
    var = cg.new_Pvariable(condition_id, template_arg)
    await cg.register_parented(var, config[CONF_ID])
    return var
