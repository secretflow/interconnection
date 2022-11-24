workspace(name = "org_interconnection")

load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")
load("@bazel_tools//tools/build_defs/repo:utils.bzl", "maybe")


maybe(
    http_archive,
    name = "com_google_protobuf",
    sha256 = "77ad26d3f65222fd96ccc18b055632b0bfedf295cb748b712a98ba1ac0b704b2",
    strip_prefix = "protobuf-3.17.3",
    type = "tar.gz",
    urls = [
        "https://github.com/protocolbuffers/protobuf/releases/download/v3.17.3/protobuf-all-3.17.3.tar.gz",
    ],
)

load("@com_google_protobuf//:protobuf_deps.bzl", "protobuf_deps")

protobuf_deps()
