from pathlib import Path
from nox_poetry import session, Session

python_versions = ["3.11", "3.10"]
@session(python=python_versions)
def tests(session: Session):
    session.install(
        "pytest",
        ".",
        "coverage")
    session.run("coverage", "run", "--parallel", "-m", "pytest", *session.posargs)
    session.notify("coverage", posargs=[])


@session(python=python_versions[0])
def coverage(session: Session) -> None:
    """Produce the coverage report."""
    session.install("coverage")

    if any(Path().glob(".coverage.*")):
        session.run("coverage", "combine")

    session.run("coverage", "report")
