"""Browser regression for the actual video and navigation examples in the guide.

Run: python -m unittest discover -s tests -p test_embedded_video_navigation.py -v
Requires Python Playwright plus Chromium with MP4 support; ffmpeg generates a
small test clip when STORIES_VIDEO_CLIP is unset. No installation is performed.
STORIES_CHROMIUM selects a system browser (otherwise Playwright's Chromium).
STORIES_VIDEO_EVIDENCE retains fixtures/results at a NEW directory; otherwise
TemporaryDirectory cleans up. Never commit supplied/private video or fixtures.
STORIES_NAVIGATION_SOURCE optionally supplies a different guide for baseline JS
comparison; the video snippet always comes from the current guide.

Native keyboard and mouse input exercise Chromium controls. Synthetic TouchEvent
checks exercise document handlers only, not a physical touchscreen or mobile UX.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import unittest


REPO = Path(__file__).resolve().parents[1]
GUIDE = REPO / "context/storyteller-instructions.md"


def fenced(text: str, heading: str, language: str) -> str:
    section = text.split("### " + heading + "\n", 1)[1].split("\n### ", 1)[0]
    return re.search(r"```" + language + r"\n(.*?)\n```", section, re.S)[1]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class EmbeddedVideoNavigation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from playwright.sync_api import sync_playwright

        cls.temp = None
        destination = os.environ.get("STORIES_VIDEO_EVIDENCE")
        if destination:
            cls.root = Path(destination).resolve()
            cls.root.mkdir(parents=True, exist_ok=False)
        else:
            cls.temp = tempfile.TemporaryDirectory(prefix="stories-video-")
            cls.addClassCleanup(cls.temp.cleanup)
            cls.root = Path(cls.temp.name)
        clip = os.environ.get("STORIES_VIDEO_CLIP")
        if clip:
            cls.clip = Path(clip).resolve()
        else:
            cls.clip = cls.root / "synthetic.mp4"
            subprocess.run([
                "ffmpeg", "-v", "error", "-f", "lavfi", "-i",
                "testsrc2=size=320x180:rate=15", "-f", "lavfi", "-i",
                "sine=frequency=440:sample_rate=44100", "-t", "20",
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac",
                "-movflags", "+faststart", str(cls.clip),
            ], check=True, timeout=60)
        cls.data = cls.clip.read_bytes()
        guide = GUIDE.read_text()
        nav_path = Path(os.environ.get("STORIES_NAVIGATION_SOURCE", str(GUIDE)))
        cls.js = fenced(nav_path.read_text(), "Navigation JavaScript", "javascript")
        cls.video = fenced(guide, "Video in HTML decks", "html")
        assert cls.video.count("REPLACE_WITH_ACTUAL_BASE64_BYTES") == 1
        video = cls.video.replace("REPLACE_WITH_ACTUAL_BASE64_BYTES",
                                 base64.b64encode(cls.data).decode())
        cls.package = cls.root / "original-package"
        cls.package.mkdir()
        cls.separate = cls.package / "Demonstration_video.mp4"
        cls.separate.write_bytes(cls.data)
        # Fixture-only CSS gives native controls/dots stable measurable dimensions.
        # The player markup and navigation logic are copied verbatim, not rewritten.
        def deck(middle):
            return """<!doctype html><meta charset="utf-8"><style>
                body { margin:0; } .slide { display:none; min-height:600px; }
                .slide.active { display:block; } video { width:640px; }
                .nav { position:fixed; bottom:12px; display:flex; gap:12px; }
                .nav-dot { width:30px; height:30px; background:#888; }
                .nav-dot.active { background:#222; }
                #counter { position:fixed; right:12px; bottom:12px; }
                </style><div class="slide active"><h1>First slide</h1></div>""" + middle + """
                <div class="slide"><h1>Last slide</h1></div>
                <div class="nav" id="nav"></div><div id="counter"></div>
                <script>""" + cls.js + "</script>"
        (cls.package / "deck.html").write_text(deck(video))
        # Move, rather than serve or use set_content: only the relocated file exists.
        cls.relocated = cls.root / "relocated"
        cls.package.rename(cls.relocated)
        cls.deck = cls.relocated / "deck.html"
        cls.separate = cls.relocated / cls.separate.name
        cls.plain = cls.relocated / "no-media.html"
        cls.plain.write_text(deck('<div class="slide"><h1>Middle slide</h1></div>'))
        cls.playwright = sync_playwright().start()
        cls.addClassCleanup(cls.playwright.stop)
        kwargs = {"headless": True}
        if os.environ.get("STORIES_CHROMIUM"):
            kwargs["executable_path"] = os.environ["STORIES_CHROMIUM"]
        cls.browser = cls.playwright.chromium.launch(**kwargs)
        cls.addClassCleanup(cls.browser.close)
        cls.evidence = {
            "guide_sha256": sha(guide.encode()), "navigation_source": str(nav_path),
            "navigation_sha256": sha(cls.js.encode()), "video_snippet_sha256": sha(cls.video.encode()),
            "clip_source": str(cls.clip), "clip_sha256": sha(cls.data),
            "clip_bytes": len(cls.data), "browser": cls.browser.version,
            "touch_scope": "synthetic DOM handler checks; not physical touchscreen",
            "audio_scope": "decoder playback only; no listening claim", "checks": {},
        }
        cls.addClassCleanup(lambda: (cls.root / "evidence.json").write_text(
            json.dumps(cls.evidence, indent=2) + "\n"))

    def setUp(self):
        self.context = self.browser.new_context(offline=True, viewport={"width": 1000, "height": 800})
        self.addCleanup(self.context.close)
        self.page = self.context.new_page()
        self.errors = []
        self.network = []
        self.page.on("pageerror", lambda error: self.errors.append(str(error)))
        self.page.on("request", lambda request: self.network.append(request.url)
                           if request.url.startswith(("http:", "https:")) else None)
        self.page.goto(self.deck.as_uri())
        self.page.set_default_timeout(10000)
        self.addCleanup(self.check_clean)

    def check_clean(self):
        self.assertEqual(self.errors, [])
        self.assertEqual(self.network, [])

    def record(self, details):
        self.evidence["checks"][self._testMethodName] = details

    def index(self):
        return self.page.evaluate("Array.from(document.querySelectorAll('.slide')).findIndex(s => s.classList.contains('active'))")

    def dot(self, number):
        self.page.locator(".nav-dot").nth(number).click()
        self.assertEqual(self.index(), number)

    def open_video(self):
        self.dot(1)
        self.page.wait_for_function("document.querySelector('video').readyState >= 2")
        return self.page.locator("video")

    def media(self):
        return self.page.locator("video").evaluate("v => ({paused:v.paused,time:v.currentTime,duration:v.duration,error:v.error?.code,ready:v.readyState})")

    def native_control(self, pseudo):
        """Locate Chromium's observed UA-shadow control, not guessed coordinates."""
        client = self.context.new_cdp_session(self.page)
        try:
            root = client.send("DOM.getDocument", {"depth": -1, "pierce": True})["root"]
            def walk(node):
                attributes = node.get("attributes", [])
                attrs = dict(zip(attributes[::2], attributes[1::2]))
                if attrs.get("pseudo") == pseudo:
                    return node
                for key in ("children", "shadowRoots"):
                    for child in node.get(key, []):
                        found = walk(child)
                        if found:
                            return found
            node = walk(root)
            self.assertIsNotNone(node, f"Native control not observed: {pseudo}")
            box = client.send("DOM.getBoxModel", {"nodeId": node["nodeId"]})["model"]["content"]
            x, y = sum(box[::2]) / 4, sum(box[1::2]) / 4
            self.assertGreater(max(box[::2]) - min(box[::2]), 0)
            self.assertGreater(max(box[1::2]) - min(box[1::2]), 0)
            return x, y
        finally:
            client.detach()

    def swipe(self, selector, start, end, cancel=False):
        self.page.locator(selector).evaluate("""(element, args) => {
            const [start,end,cancel] = args;
            const touch = x => new Touch({identifier:1,target:element,screenX:x,clientX:x,clientY:100});
            element.dispatchEvent(new TouchEvent('touchstart',{bubbles:true,touches:[touch(start)],changedTouches:[touch(start)]}));
            if (cancel) element.dispatchEvent(new TouchEvent('touchcancel',{bubbles:true}));
            element.dispatchEvent(new TouchEvent('touchend',{bubbles:true,touches:[],changedTouches:[touch(end)]}));
        }""", [start, end, cancel])

    def test_package_bytes_and_relocated_offline_playback(self):
        source = self.deck.read_text()
        embedded = re.search(r'src="data:video/mp4;base64,([^"]+)"', source)[1]
        self.assertEqual(base64.b64decode(embedded), self.separate.read_bytes())
        self.assertEqual(self.separate.read_bytes(), self.data)
        self.assertFalse(self.package.exists())
        video = self.open_video()
        video.focus()
        self.page.keyboard.press("Space")
        self.page.wait_for_function("document.querySelector('video').currentTime > 0.2")
        self.assertEqual(self.index(), 1)
        self.assertIsNone(self.media()["error"])
        self.record({"offline_file": self.deck.as_uri(), "playback": self.media(), "identical_bytes": True})

    def test_native_keyboard_click_and_seek_do_not_navigate(self):
        video = self.open_video()
        video.focus()
        self.page.keyboard.press("Space")
        self.page.wait_for_function("!document.querySelector('video').paused && document.querySelector('video').currentTime > 0.2")
        self.assertEqual(self.index(), 1)
        self.page.keyboard.press("Space")
        self.page.wait_for_function("document.querySelector('video').paused")
        before = self.media()["time"]
        self.page.keyboard.press("ArrowRight")
        # Chromium seeks by a duration-dependent increment; do not assume 5s.
        self.page.wait_for_function("before => document.querySelector('video').currentTime > before",
                                    arg=before)
        self.assertEqual(self.index(), 1)
        forward = self.media()["time"]
        self.page.keyboard.press("ArrowLeft")
        self.assertEqual(self.index(), 1)
        self.assertLess(self.media()["time"], forward)
        self.page.mouse.move(*self.native_control("-webkit-media-controls-play-button"))
        play = self.native_control("-webkit-media-controls-play-button")
        self.page.mouse.click(*play)
        self.page.wait_for_function("!document.querySelector('video').paused")
        self.assertEqual(self.index(), 1)
        timeline = self.native_control("-webkit-media-controls-timeline")
        self.page.mouse.click(*timeline)
        self.page.wait_for_function("document.querySelector('video').currentTime > document.querySelector('video').duration * 0.25")
        self.assertEqual(self.index(), 1)
        self.record({"keyboard_seek_before": before, "keyboard_seek_after": forward,
                     "observed_play_center": play, "observed_timeline_center": timeline,
                     "after_native_seek": self.media()})

    def test_slide_exit_pauses_return_preserves_and_hidden_play_is_stopped(self):
        video = self.open_video()
        video.focus()
        self.page.keyboard.press("Space")
        self.page.wait_for_function("document.querySelector('video').currentTime > 0.3")
        self.dot(2)
        state = self.media()
        self.assertTrue(state["paused"])
        self.dot(1)
        self.assertTrue(self.media()["paused"])
        self.assertAlmostEqual(self.media()["time"], state["time"], delta=0.05)
        self.dot(2)
        # Real play request/event on hidden media, not a fake 'play' dispatch.
        video.evaluate("async v => {try {await v.play()} catch(e) {if(e.name !== 'AbortError') throw e}}")
        self.page.wait_for_function("document.querySelector('video').paused")
        self.assertEqual(self.index(), 2)
        self.record({"paused_position": state["time"], "hidden_play_paused": True})

    def test_nonmedia_navigation_and_synthetic_touch_handlers(self):
        self.page.keyboard.press("ArrowRight")
        self.assertEqual(self.index(), 1)
        self.page.keyboard.press("ArrowLeft")
        self.assertEqual(self.index(), 0)
        self.page.keyboard.press("Space")
        self.assertEqual(self.index(), 1)
        # Locator hit-tested clicks in the nonmedia slide heading, on either half.
        heading = self.page.locator(".slide.active h2")
        box = heading.bounding_box()
        self.page.mouse.click(box["x"] + box["width"] * 0.8, box["y"] + box["height"] / 2)
        self.assertEqual(self.index(), 2)
        heading = self.page.locator(".slide.active h1")
        box = heading.bounding_box()
        self.page.mouse.click(box["x"] + box["width"] * 0.2, box["y"] + box["height"] / 2)
        self.assertEqual(self.index(), 1)
        self.swipe("video", 900, 100)
        self.assertEqual(self.index(), 1)
        self.swipe(".slide.active h2", 900, 100)
        self.assertEqual(self.index(), 2)
        self.swipe(".slide.active h1", 100, 900)
        self.assertEqual(self.index(), 1)
        self.swipe(".slide.active h2", 900, 100, cancel=True)
        self.assertEqual(self.index(), 1)
        self.swipe(".slide.active h2", 400, 420)
        self.assertEqual(self.index(), 1)
        self.record({"keyboard_click_dots": True, "synthetic_swipe_media_exclusion_cancel_threshold": True})

    def test_no_media_deck_navigation(self):
        self.page.goto(self.plain.as_uri())
        self.assertEqual(self.page.locator("video,audio").count(), 0)
        self.page.keyboard.press("ArrowLeft")
        self.assertEqual(self.index(), 2)
        self.page.keyboard.press("ArrowRight")
        self.assertEqual(self.index(), 0)
        self.page.keyboard.press("Space")
        self.assertEqual(self.index(), 1)
        self.dot(0)
        heading = self.page.locator(".slide.active h1")
        box = heading.bounding_box()
        self.page.mouse.click(box["x"] + box["width"] * 0.8, box["y"] + box["height"] / 2)
        self.assertEqual(self.index(), 1)
        self.swipe(".slide.active h1", 900, 100)
        self.assertEqual(self.index(), 2)
        self.assertEqual(self.page.locator("#counter").inner_text(), "3 / 3")
        self.record({"arrows_wrap_space_dot_click_synthetic_swipe_counter": True})


if __name__ == "__main__":
    unittest.main(verbosity=2)
