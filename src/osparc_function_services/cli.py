import typer

from ._utils import run_as_service
from .sensitivity_ua_services import (
    sensitivity_ua_linear_regression,
    sensitivity_ua_test_func,
)

main = typer.Typer()


@main.command()
def test_func():
    run_as_service(sensitivity_ua_test_func)


@main.command()
def linear_regression():
    run_as_service(sensitivity_ua_linear_regression)


if __name__ == "__main__":
    main()
