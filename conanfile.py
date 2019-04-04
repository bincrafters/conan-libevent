#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration


class LibeventConan(ConanFile):
    name = "libevent"
    version = "2.1.8"
    description = "libevent - an event notification library"
    topics = ("conan", "libevent", "event")
    url = "https://github.com/bincrafters/conan-libevent"
    homepage = "https://github.com/libevent/libevent"
    author = "Bincrafters <bincrafters@gmail.com>"
    license = "BSD-3-Clause"
    exports = ["LICENSE.md"]
    exports_sources = ["CMakeLists.txt"]
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False],
               "fPIC": [True, False],
               "with_openssl": [True, False],
               "disable_threads": [True, False]}
    default_options = {"shared": False,
                       "fPIC": True,
                       "with_openssl": True,
                       "disable_threads": False}
    generators = "cmake"
    _source_subfolder = "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        if self.settings.os == "Windows" and \
           self.options.shared:
            raise ConanInvalidConfiguration("libevent does not support shared on Windows")
        if self.options.with_openssl and self.options.shared:
            # static OpenSSL cannot be properly detected because libevent picks up system ssl first
            # so enforce shared openssl
            self.output.warn("Enforce shared OpenSSL for shared build")
            self.options["OpenSSL"].shared = self.options.shared

    def requirements(self):
        if self.options.with_openssl:
            self.requires.add("OpenSSL/1.0.2r@conan/stable")

    def source(self):
        checksum = "316ddb401745ac5d222d7c529ef1eada12f58f6376a66c1118eee803cb70f83d"
        tools.get("{0}/archive/release-{1}-stable.tar.gz".format(self.homepage, self.version), sha256=checksum)
        extracted_folder = "libevent-release-{}-stable".format(self.version)
        os.rename(extracted_folder, self._source_subfolder)

    def imports(self):
        # Copy shared libraries for dependencies to fix DYLD_LIBRARY_PATH problems
        #
        # Configure script creates conftest that cannot execute without shared openssl binaries.
        # Ways to solve the problem:
        # 1. set *LD_LIBRARY_PATH (works with Linux with RunEnvironment
        #     but does not work on OS X 10.11 with SIP)
        # 2. copying dylib's to the build directory (fortunately works on OS X)

        if self.settings.os == "Macos":
            self.copy("*.dylib*", dst=self._source_subfolder, keep_path=False)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["EVENT__BUILD_SHARED_LIBRARIES"] = self.options.shared
        cmake.definitions["EVENT__DISABLE_DEBUG_MODE"] = self.settings.build_type == "Release"
        cmake.definitions["EVENT__DISABLE_OPENSSL"] = self.options.with_openssl
        cmake.definitions["EVENT__DISABLE_BENCHMARK"] = True
        cmake.definitions["EVENT__DISABLE_TESTS"] = True
        cmake.definitions["EVENT__DISABLE_REGRESS"] = True
        cmake.definitions["EVENT__DISABLE_SAMPLES"] = True
        cmake.configure()
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.libs.extend(["m", "pthread"])

        if self.settings.os == "Windows":
            self.cpp_info.libs.append('ws2_32')
            if self.options.with_openssl:
                self.cpp_info.defines.append('EVENT__HAVE_OPENSSL=1')
