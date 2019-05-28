#!/usr/bin/env python
# -*- coding: utf-8 -*-
from bincrafters import build_template_default
import platform
import copy

if __name__ == "__main__":
    builder = build_template_default.get_builder(pure_c=True)
    for settings, options, env_vars, build_requires, reference in reversed(builder.items):
        if settings["build_type"] == "Release":
            new_options = copy.copy(options)
            new_options["libevent:with_openssl"] = False
            builder.add(settings, new_options, env_vars, build_requires)
    builder.run()
