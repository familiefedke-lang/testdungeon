## GameEngine.gd – turn-resolution and game-state orchestrator.
##
## Mirrors src/engine.py Engine (renamed to avoid conflict with Godot's
## built-in Engine singleton).
##
## Responsibilities:
##   - Holds game_map, player, floor_num, messages.
##   - new_game() / _next_floor() lifecycle.
##   - try_player_command(cmd) for player-turn resolution.
##   - enemy_turns() for enemy-turn resolution.
##   - update(dt) for per-frame animation ticks.
##   - Equipment bonus helpers _power() / _armor().

class_name GameEngine
extends RefCounted

const MAX_MESSAGES: int = 200

var animation_db: AnimationDB
var game_map: GameMap
var player: Actor
## Current dungeon floor number (floor_num avoids shadowing built-in floor()).
var floor_num: int
var messages: Array       ## Array[String]
var running: bool

var items_db: ItemsDB
var enemies_db: EnemiesDB


func _init(
	anim_db: AnimationDB,
	items_db_: ItemsDB,
	enemies_db_: EnemiesDB
) -> void:
	animation_db = anim_db
	items_db = items_db_
	enemies_db = enemies_db_
	game_map = null
	player = null
	floor_num = 0
	messages = []
	running = true


## ── Setup ─────────────────────────────────────────────────────────────────────

func new_game() -> void:
	floor_num = 0
	messages.clear()
	player = null
	_next_floor()


func _next_floor() -> void:
	floor_num += 1
	var rng := RandomNumberGenerator.new()
	var result: Array = Procgen.generate_floor(floor_num, enemies_db, rng)
	game_map = result[0]
	var sx: int = result[1]
	var sy: int = result[2]

	if player == null:
		player = Actor.new(
			sx, sy,
			Fighter.new(30, 5),
			SpriteComponent.new("player", "idle", "S"),
			null,
			"player"
		)
	else:
		player.x = sx
		player.y = sy

	_log("You descend to floor %d." % floor_num)


## ── Derived stat helpers ──────────────────────────────────────────────────────

func _equipment_bonuses(actor: Actor) -> Dictionary:
	var bonuses: Dictionary = {}
	for slot: String in actor.equipment.slots:
		var item_key: String = actor.equipment.slots[slot]
		var item_def = items_db.find(item_key)
		if item_def == null:
			continue
		for stat: String in item_def.bonuses:
			bonuses[stat] = bonuses.get(stat, 0) + item_def.bonuses[stat]
	return bonuses


func _armor(actor: Actor) -> int:
	return int(_equipment_bonuses(actor).get("armor", 0))


func _power(actor: Actor) -> int:
	var base: int = actor.fighter.base_power
	var bonus: int = int(_equipment_bonuses(actor).get("power", 0))
	return base + bonus


## ── Per-frame update (animations) ────────────────────────────────────────────

func update(dt: float) -> void:
	if player != null:
		player.sprite.update(dt, animation_db)
	if game_map != null:
		for entity in game_map.entities:
			if entity is Actor and entity.sprite != null:
				entity.sprite.update(dt, animation_db)


## ── Turn resolution ───────────────────────────────────────────────────────────

func try_player_command(cmd: InputHandler.Command) -> bool:
	if cmd.type == InputHandler.CommandType.QUIT:
		running = false
		return false

	if player != null and not player.is_alive():
		return false

	match cmd.type:
		InputHandler.CommandType.MOVE:
			return _handle_move(cmd.dx, cmd.dy)
		InputHandler.CommandType.USE_STAIRS:
			return _handle_use_stairs()
		InputHandler.CommandType.PICKUP:
			return _handle_pickup()

	return false


func _handle_move(dx: int, dy: int) -> bool:
	var p: Actor = player
	var nx: int = p.x + dx
	var ny: int = p.y + dy

	if not game_map.in_bounds(nx, ny):
		return false

	var target = game_map.actor_at(nx, ny)
	if target != null:
		var atk_power: int = _power(p)
		var tgt_armor: int = _armor(target)
		var damage: int = max(0, atk_power - tgt_armor)

		var dealt: int = p.fighter.attack(target, damage)
		_log("You attack %s for %d damage." % [target.name, dealt])
		if target.fighter.is_dead():
			_log("%s dies." % target.name)
			_remove_dead()
		p.sprite.set_facing_from_delta(dx, dy)
		return true

	if game_map.is_walkable(nx, ny):
		p.x = nx
		p.y = ny
		p.sprite.set_facing_from_delta(dx, dy)
		p.sprite.play("walk", 0.12)
		return true

	return false


func _handle_use_stairs() -> bool:
	var tile: int = game_map.get_tile(player.x, player.y)
	if tile == GameMap.TileType.STAIRS:
		_next_floor()
		return true
	return false


func _handle_pickup() -> bool:
	var px: int = player.x
	var py: int = player.y

	var found = null
	for e in game_map.entities:
		if e is Item and e.x == px and e.y == py:
			found = e
			break

	if found == null:
		_log("Nothing here to pick up.")
		return false

	game_map.entities.erase(found)
	player.inventory.add(found.item_key)

	var item_def = items_db.find(found.item_key)
	if item_def != null and item_def.equip_slot != null:
		if player.equipment.equip(item_def.equip_slot, found.item_key):
			_log("You pick up and equip %s." % item_def.name)
			return true

	_log("You pick up %s." % found.name)
	return true


func enemy_turns() -> void:
	if not player.is_alive():
		return

	for entity in game_map.entities.duplicate():
		if entity is Actor:
			if entity.is_alive() and entity.ai != null:
				entity.ai.take_turn(player, game_map)
				if not player.is_alive():
					_log("You die!")
					running = false
					break

	_remove_dead()


## ── Helpers ───────────────────────────────────────────────────────────────────

func _remove_dead() -> void:
	var alive: Array = []
	for e in game_map.entities:
		if e is Actor and not e.is_alive():
			continue
		alive.append(e)
	game_map.entities = alive


func _log(message: String) -> void:
	messages.append(message)
	if messages.size() > MAX_MESSAGES:
		messages = messages.slice(messages.size() - MAX_MESSAGES)
