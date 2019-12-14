import pytest


@pytest.fixture()
def main_loaded(confd, project_version_file, framework_dir, mocker):
    import dodoo
    from dodoo import RUNMODE, main

    orig_framework = dodoo._framework
    mocker.patch("dodoo.create_custom_schema_layout")
    main(framework_dir, confd, False, RUNMODE.Production, 0, project_version_file)
    yield
    dodoo._framework = orig_framework
