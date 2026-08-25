# Overlord model ripper

Imports the resource packs of Overlord (2007) into Blender: models, skeletons, skinning, textures,
animations, audio and lua byte code. The file format notes gathered while reverse engineering the
coordinate systems and the animation encoding live in [docs/FORMAT.md](docs/FORMAT.md).

# Requirements

## Blender 4.0 – 5.0

Tested with Blender 5.0.1; the code keeps the legacy action API for Blender 4.0 – 4.3.
Download : https://www.blender.org/download/

No separate Python installation is needed, the scripts run inside Blender's bundled Python.

# How to use

1. Download the repository:
    - Use git clone or download the project as a ZIP file and extract it.
2. Open the project
    - Open `Blender.blend` with Blender.
3. Configure the script:
    - The text editor on the left shows the launcher script `OverLord_launcher.py`.
    - Edit the `SOURCE_FILE` variable at the top to point to your source file
      (`.prp` / `.pvp` / `.psp` resource pack, `.omp` map, or a `.anim` exported earlier).
    - Or, to keep your local path out of the `.blend`: create `local_settings.py` next to `Blender.blend`
      (ignored by git) containing `SOURCE_FILE = r"D:\...\Character Khan.prp"`; the launcher prefers it.
4. Execute
    - Click the Run Script (play icon) button (Alt+P).
    - Save the result with `File > Save As` to a new `.blend`, so `Blender.blend` stays an empty template.
5. Result
    - Every model of the file ends up in its own collection: an armature (if the model is skinned) with
      its meshes parented to it, textured materials, and one Blender action per animation
      (`Dope Sheet > Action Editor` to switch between them; actions are kept with a fake user).
    - Models are converted to Blender's coordinate system (Z up, characters face -Y, `L_*` bones on +X),
      so nothing has to be rotated afterwards.
    - Images, animations (`.anim`), audio and lua byte code are saved into a new folder (named after the
      source file) created in the same directory as your source file.
6. Shared animations
    - Many characters use the skeleton of `Human Standard [Shared].prp`. To play one of those
      animations on a character from another file: import the character, select its armature,
      point `SOURCE_FILE` to the wanted `<file>/animations/<name>.anim` and run the script again.

## Settings

At the top of `OverLord.py`:

| setting | meaning |
|---|---|
| `ORIENT_BONES_TO_CHILDREN` | `True`: Blender bones point at their child bones (normal looking rig). `False`: bones keep the exact local axes of the game skeleton. Animation and skinning are identical either way. |
| `IMPORT_CUSTOM_NORMALS` | Import the vertex normals stored in the file as custom split normals. |
| `SCENE_FPS` | Scene frame rate; `None` keeps the frame rate of the file (15 fps). Keys are rescaled for other rates. |
| `ANIMATION_MATCH_THRESHOLD` | Minimal fraction of an animation's bones that must exist in a skeleton before it is attached to it. |

The importer itself is `OverLord.py` plus the modules in `prpUnpackerLibraries/`; the launcher inside
the `.blend` reloads them on every run, so edits are picked up without restarting Blender. `OverLord.py`
can also be run directly from Blender's text editor (edit the path at the bottom of the file).
