"""Build the mkdocs gallery page from example scripts and their matplotlib output images."""

import os
import shutil
import pathlib
from typing import TypedDict

__dirname__ = pathlib.Path(__file__).parent


class GalleryEntry(TypedDict):
    """Type definition for gallery entries."""

    script_name: str
    image_relpath: str
    github_url: str
    title_str: str


# =============================================================================
#
# =============================================================================

GITHUB_BASE = "https://github.com/vispy/GSP_API/blob/main/examples"

BLACKLISTED_BASENAMES = {
    "session_01_record_example.py",
    "session_02_player_example.py",
}


# =============================================================================
#
# =============================================================================


def main() -> None:
    """Generate mkdocs_source/gallery.md and copy matching matplotlib images."""
    root = __dirname__.parent
    examples_dir = root / "examples"
    output_dir = examples_dir / "output"
    gallery_dir = root / "mkdocs_source" / "gallery" / "images"
    gallery_dir.mkdir(parents=True, exist_ok=True)

    script_absnames = sorted(
        f for f in examples_dir.iterdir() if f.is_file() and f.suffix == ".py" and not f.name.startswith("_") and f.name not in BLACKLISTED_BASENAMES
    )

    # =============================================================================
    # Build gallery_entries list[GalleryEntry]
    # =============================================================================
    gallery_entries: list[GalleryEntry] = []
    for script_absname in script_absnames:
        script_stem = script_absname.stem
        image_paths = sorted(output_dir.glob(f"{script_stem}_*matplotlib.png"))
        for image_path in image_paths:
            image_dest_path = gallery_dir / image_path.name
            shutil.copy2(image_path, image_dest_path)
            # append gallery entry
            gallery_entry = GalleryEntry(
                script_name=script_absname.name,
                image_relpath=image_dest_path.relative_to(root / "mkdocs_source" / "gallery").as_posix(),
                github_url=f"{GITHUB_BASE}/{script_absname.name}",
                title_str=script_stem.replace("_", " ").title(),
            )
            gallery_entries.append(gallery_entry)

    # =============================================================================
    # Build Html
    # =============================================================================
    html_lines = [
        "# Examples Gallery",
        "",
        '<div class="gallery-grid">',
        "",
    ]
    for gallery_entry in gallery_entries:
        html_lines += [
            '<div class="gallery-card">',
            f'  <a href="{gallery_entry["github_url"]}" target="_blank">',
            f'    <img src="{gallery_entry["image_relpath"]}" alt="{gallery_entry["title_str"]}">',
            f'    <p>{gallery_entry["script_name"]}</p>',
            "  </a>",
            "</div>",
            "",
        ]
    html_lines += ["</div>", ""]

    gallery_md = root / "mkdocs_source" / "gallery.md"
    gallery_md.write_text("\n".join(html_lines))
    print(f"Generated {gallery_md.relative_to(root)} with {len(gallery_entries)} entries")


if __name__ == "__main__":
    main()
