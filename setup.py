# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import os

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))

long_description = []
with open(os.path.join("README.md")) as f:
    long_description.append(f.read())
with open(os.path.join("CHANGES.md")) as f:
    long_description.append(f.read())


setup(
    name="dodoo",
    description="Beautiful, robust and extensible Odoo server API "
    "extension suite for DevOps.",
    long_description="\n".join(long_description),
    use_scm_version=True,
    packages=["dodoo"],
    include_package_data=True,
    setup_requires=["setuptools_scm"],
    install_requires=[
        "click",
        "click-plugins",
        "ipdb",  # For (mostly) decent !lightweight! debugging
    ],
    license="LGPLv3+",
    author="XOE Corp. SAS",
    author_email="info@xoe.solutions",
    url="http://github.com/xoe-labs/dodoo",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: "
        "GNU Lesser General Public License v3 or later (LGPLv3+)",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Framework :: Odoo",
    ],
    entry_points="""
        [console_scripts]
        dodoo=dodoo.cli:main
        [dodoo.cli_plugins]
    """,
)
