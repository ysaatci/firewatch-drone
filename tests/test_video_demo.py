import pytest

np = pytest.importorskip("numpy")
pytest.importorskip("cv2")  # only runs with the [detection] extra installed

from firewatch.detection.infer import Detection  # noqa: E402
from firewatch.detection.video_demo import PANEL_W, annotate  # noqa: E402
from firewatch.geo.geolocate import Camera, DronePose  # noqa: E402


def test_annotate_adds_panel_and_draws():
    frame = np.zeros((360, 640, 3), dtype=np.uint8)
    pose = DronePose(51.52, 0.21, 120.0, 0.0)
    cam = Camera(640, 360, hfov=70, pitch=45)
    dets = [Detection("fire", 0.9, 100, 100, 200, 200)]

    out = annotate(frame.copy(), dets, pose, cam, t=1.0)

    assert out.shape == (360, 640 + PANEL_W, 3)
    assert out[:, :PANEL_W].any()  # panel has text
    assert out[:, PANEL_W:].any()  # box drawn on the frame


def test_annotate_with_no_detections():
    frame = np.zeros((360, 640, 3), dtype=np.uint8)
    out = annotate(frame, [], DronePose(51.52, 0.21, 120.0, 0.0), Camera(640, 360, 70, 45), 0.0)
    assert out.shape == (360, 640 + PANEL_W, 3)
