## InputHandler.gd – command objects and Godot InputEvent → Command converter.
##
## Mirrors src/input/input_handler.py.
## Returns a Command (inner class) from handle_event(), or null for no action.

class_name InputHandler
extends RefCounted


## ── Command types ─────────────────────────────────────────────────────────────

enum CommandType { MOVE, USE_STAIRS, PICKUP, QUIT }


class Command extends RefCounted:
	var type: int          ## CommandType
	var dx: int = 0
	var dy: int = 0

	func _init(t: int, dx_: int = 0, dy_: int = 0) -> void:
		type = t
		dx = dx_
		dy = dy_


## ── Factory helpers (mirror Python frozen dataclasses) ───────────────────────

static func make_move(dx: int, dy: int) -> Command:
	return Command.new(CommandType.MOVE, dx, dy)

static func make_use_stairs() -> Command:
	return Command.new(CommandType.USE_STAIRS)

static func make_pickup() -> Command:
	return Command.new(CommandType.PICKUP)

static func make_quit() -> Command:
	return Command.new(CommandType.QUIT)


## ── Key → direction map (mirrors _KEY_TO_MOVE in Python) ────────────────────

## Keycodes → Vector2i(dx, dy)
const _KEY_TO_MOVE: Dictionary = {
	KEY_UP:    Vector2i(0,  -1),
	KEY_DOWN:  Vector2i(0,   1),
	KEY_LEFT:  Vector2i(-1,  0),
	KEY_RIGHT: Vector2i(1,   0),
	# Vi-keys
	KEY_K: Vector2i(0,  -1),
	KEY_J: Vector2i(0,   1),
	KEY_H: Vector2i(-1,  0),
	KEY_L: Vector2i(1,   0),
	# Numpad cardinal
	KEY_KP_8: Vector2i(0,  -1),
	KEY_KP_2: Vector2i(0,   1),
	KEY_KP_4: Vector2i(-1,  0),
	KEY_KP_6: Vector2i(1,   0),
	# Numpad diagonal
	KEY_KP_7: Vector2i(-1, -1),
	KEY_KP_9: Vector2i(1,  -1),
	KEY_KP_1: Vector2i(-1,  1),
	KEY_KP_3: Vector2i(1,   1),
}


## Convert a Godot InputEvent to a Command, or return null.
func handle_event(event: InputEvent):
	if event is InputEventKey and event.pressed and not event.echo:
		return _handle_keydown(event as InputEventKey)
	return null


func _handle_keydown(event: InputEventKey):
	var key: int = event.keycode

	# Quit
	if key in [KEY_ESCAPE, KEY_Q]:
		return make_quit()

	# Use stairs / wait
	if key in [KEY_PERIOD, KEY_KP_5]:
		return make_use_stairs()

	# Pick up item
	if key == KEY_E:
		return make_pickup()

	# Movement
	if _KEY_TO_MOVE.has(key):
		var d: Vector2i = _KEY_TO_MOVE[key]
		return make_move(d.x, d.y)

	return null
