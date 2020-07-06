from conans import ConanFile, CMake, tools
import glob
import os


class OpenEXRConan(ConanFile):
    name = "openexr"
    version = "2.3.0"
    description = "OpenEXR is a high dynamic-range (HDR) image file format developed by Industrial Light & " \
                  "Magic for use in computer imaging applications."
    topics = ("conan", "openexr", "hdr", "image", "picture")
    license = "BSD-3-Clause"
    homepage = "https://github.com/openexr/openexr"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "namespace_versioning": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "namespace_versioning": True, "fPIC": True}
    generators = "cmake"
    exports_sources = ["CMakeLists.txt", "patches/*.patch"]

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def requirements(self):
        self.requires("zlib/1.2.11")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("openexr-{}".format(self.version), self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.definitions["OPENEXR_BUILD_PYTHON_LIBS"] = False
        self._cmake.definitions["BUILD_ILMBASE_STATIC"] = not self.options.shared
        self._cmake.definitions["OPENEXR_BUILD_SHARED"] = self.options.shared
        self._cmake.definitions["OPENEXR_BUILD_STATIC"] = not self.options.shared
        self._cmake.definitions["OPENEXR_NAMESPACE_VERSIONING"] = self.options.namespace_versioning
        self._cmake.definitions["OPENEXR_ENABLE_TESTS"] = False
        self._cmake.definitions["OPENEXR_FORCE_CXX03"] = False
        self._cmake.definitions["OPENEXR_BUILD_UTILS"] = False
        self._cmake.definitions["ENABLE_TESTS"] = False
        self._cmake.definitions["OPENEXR_BUILD_TESTS"] = False

        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    def build(self):
        self._patch_sources()

        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE*", src=self._source_subfolder, dst="licenses", ignore_case=True, keep_path=False)

        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

        with tools.chdir(os.path.join(self.package_folder, "lib")):
            for filename in glob.glob("*.la"):
                os.unlink(filename)

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "OpenEXR"
        self.cpp_info.names["cmake_find_package_multi"] = "OpenEXR"
        self.cpp_info.names["pkg_config"] = "OpenEXR"

        self.cpp_info.libs = tools.collect_libs(self)

        self.cpp_info.includedirs = [os.path.join("include", "OpenEXR"), "include"]

        if self.options.shared and self.settings.os == "Windows":
            self.cpp_info.defines.append("OPENEXR_DLL")

        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("pthread")
