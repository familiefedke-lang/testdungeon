# testdungeon

A sprite-based roguelike available in two implementations:

| Implementation | Language | Engine | Entry point |
|---|---|---|---|
| **Python** (original) | Python 3 + pygame | pygame | `python -m src.main` |
| **Godot port** | GDScript | Godot 4.5 | open `godot/` in the Godot editor |

---

## Godot 4.5 port (`godot/`)

### Quick start

1. Install [Godot 4.5](https://godotengine.org/download).
2. Open the Godot editor, choose **Import**, and select the `godot/` folder.
3. Press **F5** (or the play button) to run.

### Godot project structure

```
godot/
├── project.godot                  # Godot project configuration
├── icon.svg
├── scenes/
│   └── main.tscn                  # Root scene (Main + Renderer nodes)
├── scripts/
│   ├── autoloads/
│   │   └── Constants.gd           # Global constants (replaces constants.py)
│   ├── ecs/
│   │   ├── Entity.gd              # Base entity
│   │   ├── Actor.gd               # Entity with Fighter + Sprite + AI
│   │   ├── Item.gd                # Ground item entity
│   │   └── components/
│   │       ├── Fighter.gd         # HP / power component
│   │       ├── SpriteComponent.gd # Animation state machine
│   │       ├── BasicAI.gd         # Greedy enemy AI
│   │       ├── InventoryComponent.gd
│   │       └── EquipmentComponent.gd
│   ├── world/
│   │   ├── GameMap.gd             # Tile grid + entity list
│   │   └── Procgen.gd             # Room-and-corridor generator
│   ├── render/
│   │   ├── Renderer.gd            # Node2D – draws via _draw()
│   │   ├── AnimationDB.gd         # Loads atlas.json frame lists
│   │   └── ItemsAtlas.gd          # Loads items.atlas.json
│   ├── input/
│   │   └── InputHandler.gd        # InputEvent → Command objects
│   ├── data/
│   │   ├── EnemiesDB.gd           # Loads enemies.json
│   │   └── ItemsDB.gd             # Loads items.json
│   ├── GameEngine.gd              # Turn resolution + game state
│   └── Game.gd                    # Main scene script (game loop)
└── assets/                        # Copies of sprites + data JSON files
```

### Architecture mapping (Python → GDScript)

| Python module | GDScript equivalent | Notes |
|---|---|---|
| `src/main.py` + `src/game.py` | `scripts/Game.gd` | `_ready()` bootstraps; `_process()` is the loop |
| `src/engine.py` `Engine` | `scripts/GameEngine.gd` | Renamed – `Engine` is a Godot built-in |
| `src/constants.py` | `scripts/autoloads/Constants.gd` | Autoloaded singleton |
| `src/ecs/entity.py` | `scripts/ecs/Entity.gd` + `Actor.gd` | `RefCounted` (auto-GC) |
| `src/ecs/item.py` | `scripts/ecs/Item.gd` | |
| `src/ecs/components/*.py` | `scripts/ecs/components/*.gd` | Direct 1-to-1 translation |
| `src/world/game_map.py` | `scripts/world/GameMap.gd` | `TileType` as inner enum |
| `src/world/procgen.py` | `scripts/world/Procgen.gd` | `Room` as inner class |
| `src/world/tiles.py` | `GameMap.TileType` enum + `WALKABLE` const | Merged into `GameMap.gd` |
| `src/render/renderer.py` | `scripts/render/Renderer.gd` | Node2D with `_draw()` |
| `src/render/animations.py` | `scripts/render/AnimationDB.gd` | |
| `src/render/spritesheet.py` | Inlined into `Renderer._blit_from_atlas()` | No separate class needed |
| `src/render/items_atlas.py` | `scripts/render/ItemsAtlas.gd` | |
| `src/input/input_handler.py` | `scripts/input/InputHandler.gd` | Command inner class |
| `src/data/enemies_db.py` | `scripts/data/EnemiesDB.gd` | |
| `src/data/items_db.py` | `scripts/data/ItemsDB.gd` | |

### Controls (unchanged from Python version)

| Key | Action |
|---|---|
| Arrow keys / HJKL / Numpad | Move / attack |
| Numpad 7/9/1/3 | Diagonal movement |
| `.` / Numpad 5 | Use stairs / wait |
| `E` | Pick up item |
| `Escape` / `Q` | Quit |

---

## Python version (`src/`)

---

## Atlas system

The game uses a single sprite sheet (`assets/sprites/atlas.png`) paired with a
JSON descriptor (`assets/sprites/atlas.json`) that tells the engine which tiles
belong to which animation.

### How tile indices work

The sprite sheet is treated as a flat grid of equally-sized tiles.  
Tiles are numbered **left-to-right, top-to-bottom**, starting at **0**.

```
tilesPerRow = 4   (example)

Row 0:  [ 0 ][ 1 ][ 2 ][ 3 ]
Row 1:  [ 4 ][ 5 ][ 6 ][ 7 ]
Row 2:  [ 8 ][ 9 ][10 ][11 ]
Row 3:  [12 ][13 ][14 ][15 ]
```

Formula: `tile_index = row * tilesPerRow + column`  (both 0-based)

### atlas.json fields

| Field | Type | Description |
|---|---|---|
| `tileSize` | int | Width **and** height of one tile in pixels (tiles must be square). |
| `tilesPerRow` | int | How many tiles fit in one row of the PNG. |
| `defaultFps` | number | Fallback animation speed used when an animation does not set its own `fps`. |
| `tiles` | object | Map of **tile type names** → atlas tile index (see below). |
| `sprites` | object | Map of **sprite keys** → animation definitions (see below). |

#### Tile type mapping

The `tiles` object maps the name of each map tile type to its zero-based index in
the sprite atlas.  This is where you configure which tile in `atlas.png` is drawn
for walls, floors, and stairs:

```json
"tiles": {
  "wall":   0,
  "floor":  1,
  "stairs": 2
}
```

Valid tile type names are `"wall"`, `"floor"`, and `"stairs"` (case-insensitive).
Use the same index formula as for sprites: `row * tilesPerRow + column`.

#### Sprite / animation structure

```jsonc
"sprites": {
  "<sprite_key>": {            // arbitrary name, e.g. "player", "goblin"
    "<anim_name>": {           // e.g. "idle", "walk", "attack", "hurt", "dead"
      "S": [<tile_index>, ...],  // South-facing frames (required as fallback)
      "N": [<tile_index>, ...],  // North-facing frames
      "E": [<tile_index>, ...],  // East-facing frames
      "W": [<tile_index>, ...],  // West-facing frames
      "fps": <number>            // optional – overrides defaultFps for this anim
    }
  }
}
```

**Facing directions** are `"S"` (south / down), `"N"` (north / up),
`"E"` (east / right), `"W"` (west / left).

**Fallback chain** when a frame list is not found:
1. Requested facing (e.g. `"N"`)
2. `"S"` (south)
3. First available facing
4. `[0]` (tile 0 as last resort)

A single-element list (`[3]`) is a static frame; a multi-element list
(`[0, 1, 2, 3]`) is a looping animation.

---

### Adapting atlas.json for a new sprite sheet

**Step 1 – set the sheet dimensions**

```json
{
  "tileSize": 32,
  "tilesPerRow": 4
}
```

Change `tileSize` to the pixel size of your tiles and `tilesPerRow` to the
number of columns in your PNG.

**Step 2 – calculate tile indices**

Draw out your sheet as a grid and apply the formula above.

**Step 3 – write the frame lists**

Replace every `[<old_index>]` or `[<old_index>, ...]` with the indices that
match your new sheet.

---

### Example: 4-direction walk sheet

> *"My tilesheet has the walking animations in rows 1, 2, 3, 4 for all
> directions (S / N / E / W) with 4 frames each."*

> **Note on row numbering:** image editors and the phrase above use **1-based**
> row numbers (first row = row 1). The tile-index formula uses **0-based** row
> numbers (first row = row 0). Substitute accordingly when applying the formula.

Sheet layout (`tilesPerRow = 4`, rows labelled 1-based as in the quote):

```
         col 0   col 1   col 2   col 3
row 1:  [  0  ] [  1  ] [  2  ] [  3  ]   ← walk South  (row index 0 in formula)
row 2:  [  4  ] [  5  ] [  6  ] [  7  ]   ← walk North  (row index 1)
row 3:  [  8  ] [  9  ] [ 10  ] [ 11  ]   ← walk East   (row index 2)
row 4:  [ 12  ] [ 13  ] [ 14  ] [ 15  ]   ← walk West   (row index 3)
```

Resulting `atlas.json`:

```json
{
  "tileSize": 32,
  "tilesPerRow": 4,
  "defaultFps": 8,
  "sprites": {
    "player": {
      "walk": {
        "S": [0, 1, 2, 3],
        "N": [4, 5, 6, 7],
        "E": [8, 9, 10, 11],
        "W": [12, 13, 14, 15],
        "fps": 8
      }
    }
  }
}
```

A ready-to-use version of this example is saved as
`assets/sprites/atlas.example.json`.

If your sheet also contains other animations (idle, attack, etc.) on additional
rows, simply add them as extra `<anim_name>` blocks under the same sprite key
and fill in the matching tile indices.

If `tilesPerRow` differs from 4 (e.g. the PNG is 8 tiles wide but each row
only uses the first 4 columns), recalculate with the actual `tilesPerRow` value:

```
row 1, col 0..3  →  indices  0,  1,  2,  3   (tilesPerRow = 8)
row 2, col 0..3  →  indices  8,  9, 10, 11
row 3, col 0..3  →  indices 16, 17, 18, 19
row 4, col 0..3  →  indices 24, 25, 26, 27
```