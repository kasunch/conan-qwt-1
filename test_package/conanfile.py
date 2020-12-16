from conans import ConanFile, CMake
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"
    _cmake = None

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.definitions["USE_CONAN_BUILD_INFO"] = "ON"
            del self._cmake.definitions["CMAKE_EXPORT_NO_PACKAGE_REGISTRY"]
            self._cmake.configure()
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def test(self):
        self.output.info("This test is only a build test!")
