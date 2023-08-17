# SPDX-FileCopyrightText: 2023-present Leah Wasser <leah@pyopensci.org>
#
# SPDX-License-Identifier: MIT

try:
    from ._version_generated import __version__
except ImportError:
    __version__ = "unreleased"
