# SPDX-License-Identifier: Apache-2.0

import unittest
import onnx.hub as hub
from onnx import ModelProto
import glob
from os.path import join
import pytest  # type: ignore
import os


@pytest.mark.skipif(
    'TEST_HUB' not in os.environ or not os.environ['TEST_HUB'],
    reason="Conserving Git LFS quota"
)
class TestModelHub(unittest.TestCase):
    def setUp(self):  # type: () -> None
        self.name = "MNIST"
        self.repo = "onnx/models:master"
        self.opset = 7

    def test_force_reload(self):  # type: () -> None
        model = hub.load(self.name, self.repo, force_reload=True)
        self.assertIsInstance(model, ModelProto)

        cached_files = list(glob.glob(join(hub.get_dir(), "**", "*.onnx"), recursive=True))
        self.assertGreaterEqual(len(cached_files), 1)

    def test_listing_models(self):  # type: () -> None
        model_info_list_1 = hub.list_models(self.repo, model="mnist", tags=["vision"])
        model_info_list_2 = hub.list_models(self.repo, tags=["vision"])
        model_info_list_3 = hub.list_models(self.repo)

        self.assertGreater(len(model_info_list_1), 1)
        self.assertGreater(len(model_info_list_2), len(model_info_list_1))
        self.assertGreater(len(model_info_list_3), len(model_info_list_2))

    def test_basic_usage(self):  # type: () -> None
        model = hub.load(self.name, self.repo)
        self.assertIsInstance(model, ModelProto)

        cached_files = list(glob.glob(join(hub.get_dir(), "**", "*.onnx"), recursive=True))
        self.assertGreaterEqual(len(cached_files), 1)

    def test_custom_cache(self):  # type: () -> None
        old_cache = hub.get_dir()
        new_cache = join(old_cache, "custom")
        hub.set_dir(new_cache)

        model = hub.load(self.name, self.repo)
        self.assertIsInstance(model, ModelProto)

        cached_files = list(glob.glob(join(new_cache, "**", "*.onnx"), recursive=True))
        self.assertGreaterEqual(len(cached_files), 1)

        hub.set_dir(old_cache)

    def test_download_with_opset(self):  # type: () -> None
        model = hub.load(self.name, self.repo, opset=12)
        self.assertIsInstance(model, ModelProto)

    def test_opset_error(self):  # type: () -> None
        self.assertRaises(AssertionError, lambda: hub.load(self.name, self.repo, opset=-1))

    def test_manifest_not_found(self):  # type: () -> None
        self.assertRaises(AssertionError, lambda: hub.load(self.name, "onnx/models:unknown", silent=True))

    def test_verify_repo_ref(self):  # type: () -> None
        # Not trusted repo:
        verified = hub._verify_repo_ref("mhamilton723/models")
        self.assertFalse(verified)

        # Not trusted repo:
        verified = hub._verify_repo_ref("onnx/models:unknown")
        self.assertFalse(verified)

        # Trusted repo:
        verified = hub._verify_repo_ref(self.repo)
        self.assertTrue(verified)

    def test_get_model_info(self):  # type: () -> None
        hub.get_model_info("mnist", self.repo, opset=8)
        hub.get_model_info("mnist", self.repo)
        self.assertRaises(AssertionError, lambda: hub.get_model_info("mnist", self.repo, opset=-1))
