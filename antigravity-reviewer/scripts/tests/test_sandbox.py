"""Credential-free contract and real namespace probes using production arguments."""
import importlib.util
import os
from pathlib import Path
import shutil
import socket
import subprocess
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location(
    "isolated_sandbox", Path(__file__).resolve().parents[1] / "run-isolated-review.py"
)
controller = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(controller)


class SandboxTests(unittest.TestCase):
    def make_args(self, root, executable="/synthetic/agy", loader="/synthetic/ld-linux", libraries=()):
        runtime = root / "runtime"
        runtime.mkdir()
        state = root / "state"
        settings = state / ".gemini/antigravity-cli/settings.json"
        settings.parent.mkdir(parents=True)
        settings.write_text("{}")
        context = root / "context.txt"
        context.write_text("SYNTHETIC_CONTEXT")
        for name, content in {
            "passwd": f"agy:x:{os.getuid()}:{os.getgid()}::/home/agy:/nonexistent\n",
            "group": f"agy:x:{os.getgid()}:\n",
            "hosts": "127.0.0.1 localhost\n",
            "nsswitch.conf": "passwd: files\ngroup: files\nhosts: files dns\n",
        }.items():
            (runtime / name).write_text(content)
        return controller.build_sandbox_args(
            runtime, root, context, state, root / "bus",
            shutil.which("bwrap") or "/synthetic/bwrap", executable, loader, libraries,
            os.path.realpath(controller.find_ca()), os.path.realpath("/etc/resolv.conf"),
        )

    def test_mount_contract(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            args = self.make_args(root, libraries=["/synthetic/libc.so.6"])
            mounts = [tuple(args[i:i + 3]) for i, arg in enumerate(args)
                      if arg in ("--bind", "--ro-bind")]
            self.assertEqual(
                [item for item in mounts if item[0] == "--bind"],
                [("--bind", str(root / "state"), "/home/agy")],
            )
            expected_readonly = {
                ("/synthetic/agy", "/runtime/bin/agy"),
                ("/synthetic/ld-linux", "/synthetic/ld-linux"),
                ("/synthetic/libc.so.6", "/runtime/lib/libc.so.6"),
                (os.path.realpath(controller.find_ca()), "/etc/ssl/certs/ca-certificates.crt"),
                (os.path.realpath("/etc/resolv.conf"), "/etc/resolv.conf"),
                (str(root / "context.txt"), "/context/context.txt"),
                (str(root / "bus"), "/auth/bus"),
                (str(root / "state/.gemini/antigravity-cli/settings.json"),
                 "/home/agy/.gemini/antigravity-cli/settings.json"),
                *((str(root / "runtime" / name), "/etc/" + name)
                  for name in ("passwd", "group", "hosts", "nsswitch.conf")),
            }
            self.assertEqual({item[1:] for item in mounts if item[0] == "--ro-bind"}, expected_readonly)
            self.assertEqual(args[-2:], ["--remount-ro", "/"])
            for flag in ("--clearenv", "--die-with-parent", "--new-session", "--unshare-pid"):
                self.assertIn(flag, args)
            self.assertNotIn("--ro-bind-try", args)

    def test_real_namespace_without_credentials(self):
        missing = [tool for tool in ("cc", "bwrap", "ldd") if not shutil.which(tool)]
        if missing:
            self.skipTest("Namespace probe dependencies unavailable: " + ", ".join(missing))
        with tempfile.TemporaryDirectory(prefix="review-sandbox-test-") as directory:
            root = Path(directory)
            source, executable = root / "probe.c", root / "probe"
            source.write_text(r'''
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
static void require(int condition, const char *message) {
    if (!condition) { fprintf(stderr, "%s (errno=%d)\n", message, errno); exit(1); }
}
static void readonly(const char *path) {
    errno = 0;
    int fd = open(path, O_WRONLY | O_CREAT, 0600);
    require(fd == -1 && errno == EROFS, path);
}
int main(int argc, char **argv) {
    require(argc == 3, "probe arguments");
    errno = 0;
    require(access(argv[1], F_OK) == -1 && errno == ENOENT, "host canary visible");
    errno = 0;
    require(fcntl(atoi(argv[2]), F_GETFD) == -1 && errno == EBADF, "inherited fd open");
    require(getenv("REVIEW_TEST_MARKER") == NULL, "host environment inherited");
    char data[32] = {0};
    int fd = open("/context/context.txt", O_RDONLY);
    require(fd >= 0 && read(fd, data, sizeof(data)-1) > 0, "context unreadable");
    close(fd);
    require(strcmp(data, "SYNTHETIC_CONTEXT") == 0, "incorrect context");
    readonly("/unexpected-write");
    readonly("/context/context.txt");
    readonly("/home/agy/.gemini/antigravity-cli/settings.json");
    fd = open("/home/agy/.gemini/antigravity-cli/replacement", O_WRONLY | O_CREAT, 0600);
    require(fd >= 0, "disposable state not writable"); close(fd);
    require(rename("/home/agy/.gemini/antigravity-cli/replacement",
                   "/home/agy/.gemini/antigravity-cli/settings.json") == -1,
            "settings replaced");
    fd = open("/tmp/disposable", O_WRONLY | O_CREAT, 0600);
    require(fd >= 0, "private tmp not writable"); close(fd);
    puts("NAMESPACE_OK");
    return 0;
}
''')
            subprocess.run([shutil.which("cc"), str(source), "-o", str(executable)],
                           check=True, capture_output=True, timeout=20, close_fds=True)
            loader, libraries = controller.elf_dependencies(str(executable), shutil.which("ldd"))
            args = self.make_args(root, str(executable), loader, libraries)
            canary = root / "host-only-canary"
            canary.write_text("PUBLIC_SYNTHETIC_MARKER")
            with socket.socket(socket.AF_UNIX) as private_bus, canary.open("rb") as inherited:
                try:
                    private_bus.bind(str(root / "bus"))
                except PermissionError as exc:
                    self.skipTest("Synthetic Unix socket unavailable in this environment: " + str(exc))
                os.set_inheritable(inherited.fileno(), True)
                process = controller.close_popen(
                    args + [loader, "--library-path", "/runtime/lib", "/runtime/bin/agy",
                            str(canary), str(inherited.fileno())],
                    stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    text=True, env=dict(os.environ, REVIEW_TEST_MARKER="SYNTHETIC"),
                )
                try:
                    stdout, stderr = process.communicate(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.communicate()
                    self.fail("Namespace probe timed out")
            unsupported = (
                "No permissions to create new namespace",
                "Creating new namespace failed: Operation not permitted",
                "setting up uid map: Permission denied",
            )
            if process.returncode and any(message in stderr for message in unsupported):
                self.skipTest("Bubblewrap namespaces unavailable in this environment: " + stderr.strip())
            self.assertEqual(process.returncode, 0, stderr)
            self.assertEqual(stdout.strip(), "NAMESPACE_OK")
            self.assertEqual((root / "context.txt").read_text(), "SYNTHETIC_CONTEXT")
            self.assertEqual((root / "state/.gemini/antigravity-cli/settings.json").read_text(), "{}")
        self.assertFalse(root.exists(), "Disposable fixture was not removed")


if __name__ == "__main__":
    unittest.main()
