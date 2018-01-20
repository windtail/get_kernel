#!/usr/bin/env python

import click
import os
import re


class SystemUtilRequiredError(click.ClickException):
    pass


class SystemUtilExecError(click.ClickException):
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


def get_single_version(mirror, ver):
    m = re.match(r"^(\d+\.\d+)", ver)
    if m is None:
        raise click.UsageError("Not valid version format: %s" % ver)
    v = float(m.group(1))
    if v > 3.0:
        folder = "v%d.x/" % int(v)
    else:
        folder = "v%f/" % v
    base_url = mirror + folder
    sign_name = "linux-%s.tar.sign" % ver
    kernel_name = "linux-%s.tar.xz" % ver

    if os.system("wget %s%s" % (base_url, sign_name)) != 0:
        raise click.SystemUtilExecError("Downloading %s failed" % sign_name)

    if os.system("wget %s%s" % (base_url, kernel_name)) != 0:
        raise click.SystemUtilExecError("Downloading %s failed" % kernel_name)

    if os.system("unxz -c %s | gpg --verify %s -" % (kernel_name, sign_name)) != 0:
        raise click.SystemUtilExecError(
            "Verifing %s failed\nYou may want to gpg --search-keys [keys without public]" % kernel_name)


@click.command("Get specific kernel version and verify")
@click.option("--mirror", "-m", help="mirror url or name, by default downloading from kernel.org", default="official")
@click.argument("versions", nargs=-1)
def cli(mirror, versions):
    check_prerequisites()
    known_mirrors = {"tsinghua": "https://mirrors.tuna.tsinghua.edu.cn/kernel/",
                     "official": "https://cdn.kernel.org/pub/linux/kernel/"}
    if mirror in known_mirrors:
        mirror = known_mirrors[mirror]
    elif re.match(r"^(https|http|ftp)://.*/$", mirror) is None:
        raise click.UsageError("Not valid mirror url format")

    for ver in versions:
        get_single_version(mirror, ver)

    if len(versions) > 0:
        click.echo("Kernel %s ready" % ",".join(versions))


if __name__ == '__main__':
    cli()
