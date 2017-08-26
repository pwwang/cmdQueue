from setuptools import setup, find_packages
import cmdQueue

setup (
	name             = 'cmdQueue',
	version          = cmdQueue.VERSION,
	description      = "A command line queue.",
	url              = "https://github.com/pwwang/cmdQueue",
	author           = "pwwang",
	author_email     = "pwwang@pwwang.com",
	license          = "Apache License Version 2.0",
	packages         = find_packages(),
	scripts          = ['bin/cqctl', 'bin/cqstat', 'bin/cqsub', 'bin/cqworker'],
	classifiers      = [
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX",
        "Operating System :: POSIX :: BSD",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ]
)