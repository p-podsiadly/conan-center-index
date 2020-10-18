from conans import ConanFile, CMake, tools
import os, shutil

class LibVpxConan(ConanFile):
    name = "libvpx"
    topics = ("conan", "video", "codec", "webm", "vpx")
    homepage = "https://www.webmproject.org/code/"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "compiler", "build_type", "arch"

    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }

    default_options = {
        "shared": False,
        "fPIC": True
    }
    
    @property
    def _source_subfolder(self):
        return "source_subfolder"

    # Subfolder of the build folder, destination for make install target
    @property
    def _install_subfolder(self):
        return "install_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.shared
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

        if "shared" in self.options and self.options.shared:
            del self.options.fPIC

    def build_requirements(self):
        if self.settings.arch in ["x86", "x86_64"]:
            self.build_requires("yasm/1.3.0")

        if self.settings.os == "Windows":
            self.build_requires("msys2/20200517")
        
    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("libvpx-{}".format(self.version), self._source_subfolder)
    
    @property
    def _target(self):
        if self.settings.compiler == "Visual Studio":
            os = "win64" if self.settings.arch == "x86_64" else "win32"
            return "{}-{}-vs{}".format(self.settings.arch, os, self.settings.compiler.version)
        elif self.settings.os == "Linux":
            return "{}-linux-gcc".format(self.settings.arch)

    @property
    def _is_debug(self):
        return "Debug" in self.settings.build_type

    def build(self):
        configure_cmd = [
            os.path.join(self.source_folder, self._source_subfolder, "configure").replace("\\", "/"),
            "--target=" + self._target,
            "--enable-debug" if self._is_debug else "--disable-debug",
            "--disable-examples",
            "--disable-docs",
            "--disable-unit-tests",
            "--disable-decode-perf-tests",
            "--disable-encode-perf-tests"
        ]

        if "shared" in self.options:
            configure_cmd.extend([
                "--enable-shared" if self.options.shared else "--disable-shared",
                "--enable-static" if not self.options.shared else "--disable-static"
            ])

        if "fPIC" in self.options:
            configure_cmd.append("--enable-pic" if self.options.fPIC else "--disable-pic")
        
        if self.settings.compiler == "Visual Studio":
            if "MT" in self.settings.compiler.runtime:
                configure_cmd.append("--enable-static-msvcrt")
        
        if self.settings.os == "Windows":
            self.run(" ".join(configure_cmd), win_bash=True)
            with tools.vcvars(self):
                self.run("make -j")
                self.run("make DESTDIR=\"{}\" install".format(self._install_subfolder))
        else:
            self.run(" ".join(configure_cmd))
            self.run("make -j")
            self.run("make DESTDIR=\"{}\" install".format(self._install_subfolder))

    def package(self):
        install_root = os.path.join(self._install_subfolder, "usr", "local")

        self.copy("*", src=os.path.join(install_root, "include"), dst="include")

        self.copy("*.lib", src=os.path.join(install_root, "lib"), dst="lib", keep_path=False)
        self.copy("*.dll", src=os.path.join(install_root, "bin"), dst="bin", keep_path=False)
        self.copy("*.a", src=os.path.join(install_root, "lib"), dst="lib", keep_path=False)
        self.copy("*.so", src=os.path.join(install_root, "lib"), dst="lib", keep_path=False)

        self.copy("LICENSE", src=self._source_subfolder, dst="licenses/")

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        