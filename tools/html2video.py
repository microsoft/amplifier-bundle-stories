#!/usr/bin/env python3
"""
HTML Presentation to MP4 Video Converter with Optional Voice-Over

This tool records an HTML presentation into an MP4 video file.
It supports optional voice-over narration using edge-tts.

Key Features:
- Records HTML slides using Playwright
- Generates voice-over from <aside class="notes"> or <div class="notes"> tags
- Synchronizes slide duration with audio length
- Merges audio and video into final MP4

Requirements:
    Playwright: uv run --with playwright
    ffmpeg/ffprobe: Must be installed on system path
    edge-tts (optional): Only needed for voice-over narration

Usage:
    # Silent mode (no voice-over) - uses min-duration per slide
    uv run --with playwright tools/html2video.py input.html output.mp4

    # With voice-over narration from speaker notes
    uv run --with playwright --with edge-tts tools/html2video.py input.html output.mp4

    # Custom voice and timing
    uv run --with playwright --with edge-tts tools/html2video.py input.html output.mp4 --voice en-GB-SoniaNeural --min-duration 3

Note: This is a CLI tool, not designed to be imported as a library.
"""

import asyncio
import argparse
import sys
import shutil
import tempfile
import subprocess
from pathlib import Path
from typing import List

# Check for Playwright (required)
try:
    from playwright.async_api import async_playwright
except ImportError:
    print("Error: 'playwright' package is not installed.")
    print("Run with: uv run --with playwright tools/html2video.py ...")
    sys.exit(1)

# Check for edge-tts (optional - only needed for voice-over)
edge_tts = None
try:
    import edge_tts as _edge_tts

    edge_tts = _edge_tts
except ImportError:
    pass  # Will check later if voice-over is requested


def check_dependencies():
    """Verify that external dependencies are available."""
    if not shutil.which("ffmpeg"):
        print("Error: 'ffmpeg' is not found on the system path.")
        sys.exit(1)

    if not shutil.which("ffprobe"):
        print("Error: 'ffprobe' is not found on the system path.")
        sys.exit(1)


async def get_audio_duration(file_path: Path) -> float:
    """Get duration of an audio file in seconds using ffprobe."""
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(file_path),
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(result.stdout.strip())
    except Exception as e:
        print(f"Error getting duration for {file_path}: {e}")
        raise RuntimeError(f"Failed to get audio duration: {e}")


async def generate_silence(duration: float, output_path: Path):
    """Generate a silence audio file of specific duration."""
    # ffmpeg -f lavfi -i anullsrc=r=24000:cl=mono -t <duration> -q:a 9 <output>
    cmd = [
        "ffmpeg",
        "-y",
        "-v",
        "error",
        "-f",
        "lavfi",
        "-i",
        "anullsrc=r=24000:cl=mono",
        "-t",
        str(duration),
        str(output_path),
    ]
    subprocess.run(cmd, check=True)


async def concatenate_audio(files: List[Path], output_path: Path):
    """Concatenate multiple audio files into one."""
    # Create a list file for ffmpeg
    list_file = output_path.parent / "audio_list.txt"
    with open(list_file, "w") as f:
        for file in files:
            f.write(f"file '{file.absolute()}'\n")

    cmd = [
        "ffmpeg",
        "-y",
        "-v",
        "error",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(list_file),
        "-c",
        "copy",
        str(output_path),
    ]
    subprocess.run(cmd, check=True)


async def process_presentation(
    html_path: str,
    output_path: str,
    min_duration: float,
    width: int,
    height: int,
    voice: str,
):
    input_file = Path(html_path).resolve()
    if not input_file.exists():
        print(f"Error: Input file '{html_path}' not found.")
        sys.exit(1)

    print(f"Processing '{input_file.name}'...")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # --- Phase 1: Analysis & Audio Generation ---
        print("Phase 1: Analyzing slides and generating audio...")

        slide_durations = []
        audio_files = []

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(viewport={"width": width, "height": height})
            await page.goto(f"file://{input_file}")
            await page.wait_for_load_state("networkidle")

            # Find slides
            slides = await page.locator(".slide").all()
            slide_count = len(slides)
            print(f"Found {slide_count} slides.")

            if slide_count == 0:
                print("Error: No slides found (.slide class). Cannot generate video.")
                print("Ensure your HTML has elements with class='slide'.")
                await browser.close()
                sys.exit(1)

            for i, slide in enumerate(slides):
                print(f"  Processing slide {i + 1}/{slide_count}...")

                # Extract notes
                notes = ""
                try:
                    # Check for .notes inside the slide
                    note_el = slide.locator(".notes")
                    if await note_el.count() > 0:
                        notes = await note_el.inner_text()
                        notes = notes.strip()
                except Exception as e:
                    print(f"    Error extracting notes: {e}")

                slide_audio_path = temp_path / f"slide_{i:03d}.mp3"
                final_slide_audio = temp_path / f"final_slide_{i:03d}.mp3"

                duration = min_duration

                if notes and edge_tts is not None:
                    print(f"    Generating voice-over ({len(notes)} chars)...")
                    # Generate TTS
                    comm = edge_tts.Communicate(notes, voice)
                    await comm.save(str(slide_audio_path))

                    audio_dur = await get_audio_duration(slide_audio_path)
                    print(f"    Audio duration: {audio_dur:.2f}s")

                    # Calculate total slide duration (audio + padding)
                    # Add 0.5s padding at end
                    target_duration = max(min_duration, audio_dur + 0.5)
                    duration = target_duration

                    # If we need padding
                    if target_duration > audio_dur:
                        pad_dur = target_duration - audio_dur
                        pad_path = temp_path / f"pad_{i:03d}.mp3"
                        await generate_silence(pad_dur, pad_path)
                        await concatenate_audio(
                            [slide_audio_path, pad_path], final_slide_audio
                        )
                    else:
                        # Should not happen given logic above, but safe copy
                        shutil.copy(slide_audio_path, final_slide_audio)
                elif notes and edge_tts is None:
                    print("    Notes found but edge-tts not installed. Using silence.")
                    print(
                        "    (For voice-over: uv run --with playwright --with edge-tts ...)"
                    )
                    await generate_silence(min_duration, final_slide_audio)
                else:
                    print("    No notes. Using silence.")
                    # Generate silence for min_duration
                    await generate_silence(min_duration, final_slide_audio)

                slide_durations.append(duration)
                audio_files.append(final_slide_audio)

            await browser.close()

        # Concatenate all audio
        full_audio_path = temp_path / "full_audio.mp3"
        await concatenate_audio(audio_files, full_audio_path)

        # --- Phase 2: Video Recording ---
        print("\nPhase 2: Recording video...")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={"width": width, "height": height},
                record_video_dir=str(temp_path),
                record_video_size={"width": width, "height": height},
            )

            page = await context.new_page()
            await page.goto(f"file://{input_file}")
            await page.wait_for_load_state("networkidle")

            # Record loop
            for i in range(slide_count):
                dur = slide_durations[i] if i < len(slide_durations) else min_duration
                print(f"  Recording slide {i + 1}/{slide_count} ({dur:.1f}s)...")

                # Wait for the calculated duration
                await asyncio.sleep(dur)

                # Advance slide
                if i < slide_count - 1:
                    await page.keyboard.press("ArrowRight")
                    # Visual transition buffer (handled in audio padding usually,
                    # but we wait a tiny bit to ensure keypress registers before next sleep)
                    # Actually, the sleep above IS the viewing time.
                    # The keypress happens at the very end.

            await context.close()
            await browser.close()

            # Find video file
            video_files = list(temp_path.glob("*.webm"))
            if not video_files:
                print("Error: No video recorded.")
                sys.exit(1)
            raw_video = video_files[0]

            # --- Phase 3: Muxing ---
            print("\nPhase 3: Merging audio and video...")

            # ffmpeg -i video.webm -i audio.mp3 -c:v libx264 -c:a aac -shortest output.mp4
            cmd = [
                "ffmpeg",
                "-y",
                "-v",
                "error",
                "-i",
                str(raw_video),
                "-i",
                str(full_audio_path),
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                "-c:a",
                "aac",
                "-shortest",  # Stop when shortest stream ends (should be equal)
                str(output_path),
            ]

            try:
                subprocess.run(cmd, check=True)
                print(f"\nSuccess! Video saved to: {output_path}")
            except subprocess.CalledProcessError as e:
                print(f"Error merging video: {e}")
                sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Convert HTML presentation to MP4 with Voice-Over"
    )
    parser.add_argument("input_file", help="Path to input HTML file")
    parser.add_argument("output_file", help="Path to output MP4 file")
    parser.add_argument(
        "--min-duration",
        type=float,
        default=5.0,
        help="Minimum duration per slide in seconds (default: 5.0)",
    )
    parser.add_argument(
        "--width", type=int, default=1920, help="Video width (default: 1920)"
    )
    parser.add_argument(
        "--height", type=int, default=1080, help="Video height (default: 1080)"
    )
    parser.add_argument(
        "--voice",
        type=str,
        default="en-US-AriaNeural",
        help="Voice ID for TTS (default: en-US-AriaNeural)",
    )

    args = parser.parse_args()

    check_dependencies()

    try:
        asyncio.run(
            process_presentation(
                args.input_file,
                args.output_file,
                args.min_duration,
                args.width,
                args.height,
                args.voice,
            )
        )
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
