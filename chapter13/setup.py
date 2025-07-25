import setuptools

setuptools.setup(
    name="nyctransport",
    version="0.1",
    description="Package containing custom Airflow components for NYC transportation project.",
    packages=setuptools.find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=["apache-airflow~=3.0"],
    python_requires=">=3.12",
)
