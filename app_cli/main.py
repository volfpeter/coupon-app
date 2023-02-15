from typer import Typer


def create_cli_app() -> Typer:
    app = Typer()

    @app.command()
    def run_fixture(id: str):
        """
        Executes the fixture with the ID.
        """
        if id == "demo":
            from .demo_fixture import run_fixture

            print("Executing demo fixture...")
            run_fixture()
        else:
            raise ValueError("Unknown fixture")

    return app


if __name__ == "__main__":
    app = create_cli_app()
    app()
