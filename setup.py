from setuptools import setup,find_packages

setup(
    name='hotpot',
    version='3.0.0',
    author='Ruta Tang',
    author_email="953259325@qq.com",
    url="https://github.com/RutaTang/Hotpot",
    description="A tiny and easy python web framework just for your fun! :)",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        'werkzeug',
        'cryptography',
        'pyjwt',
        "MarkupSafe",
    ],
    python_requires=">=3.6",
)
