import subprocess


def post_install() -> None:
    subprocess.run(["poetry", "run", "pre-commit", "install"], check=True)
