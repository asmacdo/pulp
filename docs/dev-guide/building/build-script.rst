Test Building Pulp and the plugins
----------------------------------

Are you ready to build something? The next step is to ensure that the build that you are going to do
has an appropriate yaml file in ``pulp_packaging/ci/config/releases/<build-name>.yaml`` (explained in
detail above). Double check for each repository that the ``git_branch`` field points to the branch or tag
that you wish to build from and that the ``version`` field is correct. The ``pulp_packaging/ci/build-all.py``
script which will perform the following actions:

#. Load the specified configuration from ``pulp_packaging/ci/config/releases``.
#. Clone all the required git repositories to the ``working/<repo_name>`` directory.
#. Check out the appropriate branch or tag for each of git repos.
#. If branch, check that the branch has been merged forward.
#. Update version in main spec file to match version in yaml config provided.
#. If on branch, merge forward the spec change using -ours strategy
#. Find all the spec files in the repositories.
#. Check koji to determine if the version in the spec already exists in koji.
#. Test build all the packages that do not already exist in koji.
#. Optionally (if ``--release`` is passed), create tag and push it to GitHub.
#. Optionally (if ``--release`` is passed), release build all the packages that do not already exist in koji.
#. Download the already existing packages from koji.
#. Download the scratch built packages from koji.
#. Assemble the repositories for all the associated distributions.
#. Optionally (if ``--disable-push`` is not passed) push the repositories to fedorapeople.

Run the build script with the following syntax::

    $ ./build-all.py <name of yaml file> [options]

For example, to perform a test build of the 2.6-dev release as specified in
``pulp_packaging/ci/config/releases/2.6-dev.py`` where the results are not pushed to
fedorapeople::

    $ ./build-all.py 2.6-dev --disable-push


