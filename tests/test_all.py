# coding: utf-8


import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import get_kernel
from click.testing import CliRunner
import pytest


def test_invalid_mirror():
    runner = CliRunner()
    result = runner.invoke(get_kernel.cli, ["-m", "invalidmirror"])
    assert result.exit_code != 0
    assert "known_mirrors" in result.output


def test_valid_mirror_no_kernel(mocker):
    mocker.patch.object(get_kernel, "check_prerequisites")
    runner = CliRunner()
    result = runner.invoke(get_kernel.cli, ["--mirror", "tsinghua"])
    assert result.exit_code == 0
    assert len(result.output) == 0


def test_invalid_kernel_verions(mocker):
    mocker.patch.object(get_kernel, "check_prerequisites")
    mocker.patch.object(get_kernel, "get_single_version", autospec=True)

    runner = CliRunner()
    result = runner.invoke(get_kernel.cli, ["2x"])
    assert result.exit_code != 0
    assert "not a valid kernel version" in result.output

    result = runner.invoke(get_kernel.cli, ["4.14.14", "v4.1"])
    assert result.exit_code != 0
    assert "not a valid kernel version" in result.output


def test_missing_required_cmd(mocker):
    mocker.patch.object(get_kernel, "exists",
                        return_value=False, autospec=True)
    runner = CliRunner()
    result = runner.invoke(get_kernel.cli)
    assert result.exit_code != 0
    assert "required" in result.output


def test_download_error(mocker):
    mocker.patch.object(get_kernel, "check_prerequisites")
    mocker.patch.object(get_kernel, "download", autospec=True,
                        side_effect=get_kernel.DownloadError("test_download_error"))
    runner = CliRunner()
    result = runner.invoke(get_kernel.cli, ["4.14.14"])
    assert result.exit_code != 0
    assert "test_download_error" in result.output


def test_success(mocker):
    mocker.patch.object(get_kernel, "check_prerequisites")
    mocker.patch.object(get_kernel, "get_single_version", autospec=True)
    runner = CliRunner()
    result = runner.invoke(get_kernel.cli, ["4.14.14", "3.18"])
    assert result.exit_code == 0
    assert "ready" in result.output
