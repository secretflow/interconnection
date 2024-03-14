# Copyright 2023 Ant Group Co., Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Ideas borrowed from: https://github.com/ray-project/ray/blob/master/python/setup.py

import io
import os
import platform
import re
import shutil
import subprocess
import sys

from setuptools import setup, find_packages

ROOT_DIR = os.path.dirname(__file__)

def find_version(*filepath):
    # Extract version information from filepath
    with open(os.path.join(ROOT_DIR, *filepath)) as fp:
        version_match = re.search(
            r"^__version__ = ['\"]([^'\"]*)['\"]", fp.read(), re.M
        )
        if version_match:
            return version_match.group(1)
        raise RuntimeError("Unable to find version string.")


def read_requirements(*filepath):
    requirements = []
    with open(os.path.join(ROOT_DIR, *filepath)) as file:
        requirements = file.read().splitlines()
    return requirements


class SetupSpec:
    def __init__(self, name: str, description: str):
        self.name: str = name
        self.version = find_version("interconnection", "version.py")
        self.description: str = description
        self.files_to_include: list = []
        self.install_requires: list = []
        self.extras: dict = {}


setup_spec = SetupSpec(
    "interconnection",
    "Interconnection aims to define standard interconnection protocols for multi-layers in privacy-preserving computing.",
)


setup_spec.install_requires = read_requirements('requirements.txt')


# Calls Bazel in PATH
def bazel_invoke(invoker, cmdline, *args, **kwargs):
    try:
        print(f'Invoke command: bazel {" ".join(cmdline)}')
        result = invoker(['bazel'] + cmdline, *args, **kwargs)
        return result
    except IOError:
        raise


def build():
    bazel_env = dict(os.environ, PYTHON3_BIN_PATH=sys.executable)

    bazel_flags = ["--verbose_failures"]

    bazel_precmd_flags = []

    bazel_targets = ["//interconnection:ic_py_proto"]

    bazel_flags.extend(["-c", "opt"])

    return bazel_invoke(
        subprocess.check_call,
        bazel_precmd_flags + ["build"] + bazel_flags + ["--"] + bazel_targets,
        env=bazel_env,
        )


# Ensure no remaining lib files.
build_dir = os.path.join(ROOT_DIR, "build")
if os.path.isdir(build_dir):
    shutil.rmtree(build_dir)

build()

setup(
    name=setup_spec.name,
    version=setup_spec.version,
    author="SecretFlow Team",
    author_email='secretflow-contact@service.alipay.com',
    description=(setup_spec.description),
    long_description=io.open(
        os.path.join(ROOT_DIR, "README.md"), "r", encoding="utf-8"
    ).read(),
    long_description_content_type='text/markdown',
    url="https://github.com/secretflow/interconnection",
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    packages=find_packages(where="bazel-bin"),
    package_dir={"": "bazel-bin"},
    install_requires=setup_spec.install_requires,
    setup_requires=["wheel"],
    extras_require=setup_spec.extras,
    license="Apache 2.0",
    options={'bdist_wheel': {'plat_name': 'any'}},
)
