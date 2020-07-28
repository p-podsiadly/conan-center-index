This section gathers the most common questions from the community related to packages and usability of this repository.

## What is the policy on recipe name collisions?

Packages generated by the build service and uploaded to Conan Center follow the structure of `<name>/<version>` for the reference. Although the ecosystem of C/C++ open-source libraries is not as big as in other languages there is still a risk of having a name collision for the names of the package.

This repository will try to follow the most well-known names for each of the recipes contributed, paying attention to all the contributions and checking any collision with other popular libraries beforehand. In the case of having to face disambiguation (due to different libraries with the same name), we would look at other sources and look for a consensus.

However, if it is not possible and there is the case of a new recipe producing a name collision, the first recipe contributed will have precedence over it. Generally, recipes contributed to the repo won't change its name in order to not break users.

For example, `GSL` is the name of `Guidelines Support Library` from Microsoft and `GNU Scientific Library` from GNU. Both libraries are commonly known as `gsl`, however, to disambiguate (if there is already a `gsl` package in this repo) we could use `ms-gsl` in the first case or `gnu-gsl` in the second.

## Should reference names use `-` or `_`?

Recipes should stick to the original name of a library as much as possible. For example `libjpeg-turbo`, `expected-lite` and `optional-lite` have a `-` in their original names.

In the case of spaces in the name, the most common approach is to use `_` as done in `xz_utils`.

For libraries with a too generic name, like `variant`, the name of the organization can be used as prefix separated by a `-`, like `mpark-variant`, `tl-expected` or `taocpp-tuple`.

## Why are CMake find/config files and pkg-config files not packaged?

We know that using `find_package()` and relying on the CMake behavior to find the dependencies is something that should be avoided in favor of the information provided by the package manager.

Conan has an abstraction over the packages build system and description by using [generators](https://docs.conan.io/en/latest/reference/generators.html). Those generators translate the information of the dependency graph and create a suitable file that can be consumed by your build system.

In the past, we have found that the logic of some of the CMake's find/config or pkg-config files can lead to broken scenarios due to issues with:

- Transitive dependencies: The find logic of CMake can lead to link libraries with system libraries instead of the ones specified in the conanfile.
- Different build type configurations: Usually those files are not prepared to handle multiconfiguration development while switching between release/debug build types for example.
- Absolute paths: Usually, those files include absolute paths that would make the package broken when shared and consumed.
- Hardcoded versions of dependencies as well as build options that make overriding dependencies from the consumer not possible.

We believe that the package manager should be the one responsible to handle this information in order to achieve a deterministic and controlled behavior.
Regarding the integration with CMake, Conan already provides ways to consume those packages in the same way by using generators like [cmake_find_package](https://docs.conan.io/en/latest/reference/generators/cmake_find_package.html)* or [cmake_find_package_multi](https://docs.conan.io/en/latest/reference/generators/cmake_find_package.html) and features like [components](https://docs.conan.io/en/latest/creating_packages/package_information.html#using-components) to define internal libraries of a package and generate proper CMake targets or [build_modules](https://docs.conan.io/en/latest/reference/conanfile/attributes.html) to package build system utilities like CMake macros.

Defining the package information in the recipe is also useful in order to consume those packages from a different build system, for example using pkg-config with the [pkg_config generator](https://docs.conan.io/en/latest/reference/generators/pkg_config.html).

Finally, by not allowing these files we make packages agnostic to the consumer as the logic of those files is not in the package but in the way the consumer wants the information.

If you really think this is an issue and there is something missing to cover the use case of a library you want to contribute to ConanCenter, please do not hesitate to open an issue and we will be happy to hear your feedback.

\* Take a look at the integrations section to learn more: https://docs.conan.io/en/latest/integrations/build_system/cmake/cmake_find_package_generator.html

## Should recipes export a recipe's license?

No, recipes do not need to export a recipe license. Recipes and all files contributed to this repository are licensed under the license in the root of the repository. Using any recipe from this repository or directly from conan-center implies the same licensing.

## Why recipes that use build tools (like CMake) that have packages in Conan Center do not use it as a build require by default?

We generally consider tools like CMake as a standard tool to have installed in your system. Having the `cmake` package as a build require in all the recipes that use it will be an overkill, as every build required is installed like a requirement and takes time to download. However, `cmake` could be useful to use in your profile:

```
[build_requires]
cmake/3.17.2
```

Other packages using more unusual build tools, like `OpenSSL` using `strawberryperl`, will have the build require in the recipe as it is likely that the user that want to build it from sources will not have it installed in their system

## Are python requires allowed in the conan-center-index?

Unless they are a general and extended utility in recipes (in which case, we should study its inclusion in the Conan tools module), python requires are not allowed in conan-center-index.

## What version should packages use for libraries without official releases?

The notation shown below is used for publishing packages where the original library does not make official releases. Thus we use a datestamp corresponding to the date of a commit. In order to create reproducible builds, we also "commit-lock" to the latest commit on that day. Otherwise, users would get inconsistent results over time when rebuilding the package. An example of this is the [NanoRange](https://github.com/tcbrindle/NanoRange) library, where its package reference is `nanorange/20191001` and its sources are locked the latest commit on that date: https://github.com/conan-io/conan-center-index/blob/master/recipes/nanorange/all/conandata.yml#L2L3

## Is the Jenkins orchestration library publicly available?

Currently, the Jenkins orchestration library for this build service is not available. We believe this solution is too specific for this purpose, as we are massively building binaries for many configurations and the main purpose of a CI system with Conan in an organization should be to rebuild only the need packages. However, we know this could be interesting for organizations in order to learn new approaches for CI flows. We will release this information and CI flow recommendations as soon as possible.

## Why not x86 binaries?

As described in the [Supported platforms and configurations](https://github.com/conan-io/conan-center-index/wiki/Supported-Platforms-And-Configurations), only the x86_64 architecture is available for download, the rest must be built from sources. The reasons behind this decision are:

* Few users need different pre-built packages that are not x86_64 packages, this number is less than 10% of total users (data obtained through the download counter from Bintray), and tends to decrease over the years;
* Some OS are putting the x86 as obsolete, examples [macOS](https://developer.apple.com/documentation/macos-release-notes/macos-catalina-10_15-release-notes) and Ubuntu 20.04;
* For security reasons, most companies build their own packages from sources, even if they already have a pre-built version available, which further reduces the need for extra configurations;
* Each recipe results in around 130 packages, and this is only for x86_64, but not all packages are used, some settings remain with zero downloads throughout their life. So, imagine adding more settings that will be rarely used, but that will consume more resources as time and storage, this leaves us in an impractical situation.

#### But if there are no packages available, what will the x86 validation look like?

As stated earlier, any increase in the number of configurations will result in an impractical scenario. In addition, more validations require more review time for a recipe, which would increase the time for all PRs, delaying the release of a new package. For these reasons, x86 is not validated by the CCI.

We often receive new fixes and improvements to the recipes already available for x86_64, including help for other architectures like x86 and ARM. In addition, we also receive new cases of bugs, for recipes that do not work on a certain platform, but that are necessary for use, which is important to understand where we should put more effort. So we believe that the best way to maintain and add support for other architectures is through the community.