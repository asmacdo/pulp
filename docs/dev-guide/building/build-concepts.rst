Building Instructions
=====================

Getting Started
---------------

There are some concepts you should internalize before you begin making builds.

Koji Tags
^^^^^^^^^

Koji has a concept called tags. A tag is essentially a grouping of package builds.
Pulp uses one Koji tag per Pulp X.Y release stream, per distribution, per architecture.
For example, the 2.6 releases of pulp will build into the pulp-2.6-<distribution> tags in koji.
You can see the full list of Pulp's Koji tags
`here <http://koji.katello.org/koji/search?match=glob&type=tag&terms=pulp*>`_.

Build config files
^^^^^^^^^^^^^^^^^^
Pulp release and testing builds are collections of components that are versioned independently.
For example, the core Pulp server may be at version 2.6 while pulp_docker may be at version 1.0.
This assembly is accomplished using release definitions specified in the
``pulp_packaging/ci/config/releases/<build-name>.yaml`` files. Each file specifies the details
of a build that the Pulp build scripts can later assemble. The components within that
file specify the target koji tag as well as the individual git repositories and branches that
will be assembled as part of a build. In addition it specifies the directory within
https://repos.fedorapeople.org/repos/pulp/pulp/testing/automation/ where the build results
will be published. The file has the following format:
::
  koji-target-prefix: pulp-2.7
  rsync-target-dir: 2.7/dev
  repositories:
    - name: pulp
      external_deps: deps/external_deps.json
      git_url: git@github.com:pulp/pulp.git
      git_branch: 2.7-dev
      version: 2.7.0-0.7.beta

``koji-target-prefix``: This target needs to exist in koji.

``rsync-target-dir``: The directory inside of
https://repos.fedorapeople.org/pulp/pulp/testing/automation/ to rsync the RPMs
when build is complete.

``repositories``: describes a list of Git repositories to include in the build.

Each repository has the following fields:

``name``: name of the project in repository. This should be the same as the name
of the root directory of a project.

``external_deps``: path inside root directory of repository of the json file describing external dependencies that need to be included in the RPM
repository at the end of build process.

``git_url``: URL used to clone a project

``git_branch``: Branch or tag to checkout after cloning the git repository

``parent_branch``: This is only used when a project is being built from a hotfix branch. This value
specifies which branch the current branch should be merged into.

``version``: The version that is being built. When building an alpha, beta, or RC the format is the
following: X.Y.Z-0.<build_number>.<alpha,beta,rc> When building a GA version the format is
X.Y.Z-<build_number>

.. note::

   For pre-release builds, Pulp uses the build number as the release field. The first pre-release build
   will always be 0.1, and every build thereafter prior to the release will be the last release plus
   0.1, even when switching from alpha to beta. For example, if we have build 7 2.5.0 alphas and it
   is time for the first beta, we would be going from 2.5.0-0.7.alpha to 2.5.0-0.8.beta. For release
   builds, use whole numbers for the build number. We loosely follow the
   `Fedora Package Versioning Scheme <http://fedoraproject.org/wiki/Packaging:NamingGuidelines#Package_Versioning>`_.

Another thing to know about Koji is that once a particular NEVRA (Name, Epoch, Version, Release,
Architecture) is built in Koji, it cannot be built again. However, it can be included in multiple
Koji tags. For example, if ``python-celery-3.1.11-1.el7.x86_64`` is built into the
``pulp-2.4-rhel7`` tag and you wish to add that exact package in the ``pulp-2.5-rhel7`` tag, you
must indicate the build to use in the version field of the release stream's definition file,
``2.5-dev.yaml`` in this case.

Because there is no way to automatically determine when a particular component needs to be rebuilt or what that version should be, the build-infrastructure assumes that whatever version is specified
in the yaml file is the final version that is required.  If a release build of that version had
already been built in koji then those RPMs will be used. If the version specified in the yaml file
does not match the version in the spec file, the spec file will be updated and the change will be
merged forward using the 'ours' strategy.


When to build from a -dev branch, a tag or hotfix branch
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

All alphas and betas are built from the -dev branch of each project. As changes are added to the
-dev branch of a project, those changes are released with the next alpha or beta. Once a beta is
considered stable, the release candidate should be built from the tag that was generated during
the build process of the stable beta. This guarantees that the RPMs generated will be exactly the
same as the ones that were part of the stable beta. Similarly, a GA release should be built from
the tag created by the release candidate.

In some situations you want to include something extra on top of the stable beta. This could be
documentation changes or a particular fix for an issue that was found after releasing the first
release candidate. In these situations either a -dev branch or a hotfix branch is used to do the
build. The -dev branch can be used only if it contains exactly the changes you'd want to have in
the build and nothing more. If other changes have been made to the -dev branch, then the changes
that need to be included in the next release candidate should be put on a hotfix branch that is
created from the tag that was created when building the previous release candidate. In the
situation where a hotfix branch is used, the yaml config should include a `parent_branch`. The
`parent_branch` in this case should be the name of the -dev branch that was used to build the
betas.

Tools used when building
^^^^^^^^^^^^^^^^^^^^^^^^

Test or release builds (with the exclusion of the signing step) may be performed using
Jenkins.  There are automated jobs that will run nightly which build repositories that can be used
for validation.  When those jobs are initiated manually there is a parameter to enable the
release build process in koji.  If a release build is performed with Jenkins you will still need
to sign the rpms and manually push them to the final location on fedorapeople.

Pulp has some helper scripts in the
`pulp_packaging/ci <https://github.com/pulp/pulp_packaging/tree/master/ci>`_ directory to assist
with builds. These wrapper scripts call `tito <https://github.com/dgoodwin/tito>`_
and `koji <https://fedoraproject.org/wiki/Koji>`_ to do the actual tagging and
build work.

Both packages are in Fedora and EPEL so you should not need to install from
source. Technically you do not need to ever call these scripts directly.
However, some familiarity with both tito and koji is good, especially when
debugging build issues.
