#!/usr/bin/env python
# coding: utf-8

import click
import os
import re


class SystemUtilRequiredError(click.ClickException):
    pass


class DownloadError(click.ClickException):
    pass


class VerifyError(click.ClickException):
    pass


def exists(cmd):
    return os.system("which " + cmd + " > /dev/null") == 0


def require(cmd):
    if not exists(cmd):
        raise SystemUtilRequiredError(cmd + " required")


def check_prerequisites():
    require("wget")
    require("unxz")
    require("gpg")
    require("tar")


def download(url, filename):
    if os.system("wget -O %s %s" % (filename, url)) != 0:
        raise DownloadError("Failed to download %s" % filename)


def verify(xzfile, signfile):
    if os.system("unxz -c %s | gpg --verify %s -" % (xzfile, signfile)) != 0:
        raise VerifyError(
            "Failed to verify %s\nYou may run `gpg --search-keys <key>` if you encounter no public key error" % xzfile)


def get_single_version(mirror, ver):
    if ver.main > 3.0:
        folder = "v%d.x/" % int(ver.main)
    else:
        folder = "v%.1f/" % ver.main

    base_url = mirror + folder
    sign_name = "linux-%s.tar.sign" % ver.full
    kernel_name = "linux-%s.tar.xz" % ver.full

    download(base_url + sign_name, sign_name)
    download(base_url + kernel_name, kernel_name)
    verify(kernel_name, sign_name)


class KernelVersion(object):
    def __init__(self, ver):
        m = re.match("^(\d+\.\d+)", ver)
        assert m is not None

        self.main = float(m.group(1))
        self.full = ver

    def __str__(self):
        return self.full


class KernelVersionParamType(click.ParamType):
    name = 'kernel_version'

    def convert(self, value, param, ctx):
        m = re.match("^(\d+\.\d+)", value)
        if m is None:
            self.fail("%s is not a valid kernel version" % value, param, ctx)
        return value


KERNEL_VERSION = KernelVersionParamType()


class MirrorParamType(click.ParamType):
    name = 'mirror'

    def __init__(self):
        self.known_mirrors = {"tsinghua": "https://mirrors.tuna.tsinghua.edu.cn/kernel/",
                              "default": "https://cdn.kernel.org/pub/linux/kernel/"}

    def convert(self, value, param, ctx):
        if value in self.known_mirrors:
            return self.known_mirrors[value]
        if re.match(r"^(https|http|ftp)://[^/]", value) is None:
            self.fail("Mirror should be valid https/http/ftp URL or known mirrors' name\n"
                      "All known_mirrors are %s" % ",".join(self.known_mirrors), param, ctx)
        if not value.endswith("/"):
            return value + "/"
        else:
            return value


MIRROR = MirrorParamType()


@click.command("Get specific kernel version and verify")
@click.option("--mirror", "-m", type=MIRROR, help="mirror name or URL, default kernel.org", default="default")
@click.argument("versions", nargs=-1, type=KERNEL_VERSION)
def cli(mirror, versions):
    check_prerequisites()

    for ver in versions:
        get_single_version(mirror, KernelVersion(ver))

    if len(versions) > 0:
        click.echo("Kernel %s ready" % ",".join(versions))


if __name__ == '__main__':
    cli()
